# Od fork: database migration notes

This file records where Od's production Cuebot database differs from the migrations in this repo, and what to do about it when the fork next merges upstream OpenCue. Read it before running `flyway migrate` for an upstream upgrade.

State when this was written (2026-10-14): the fork's migrations stop at `V34__Add_loki_job_fields.sql`. Upstream OpenCue is at `V51`. odfarm01's database `cuebot_local` was loaded by hand rather than by Flyway. It was verified against the migrations and then baselined in Flyway at version 34 (OP-1130), so `flyway_schema_history` has a baseline row for 34 and nothing pending.

## 1. `layer.str_range` is wider on odfarm01 than in the migrations

- Live: `layer.str_range` is `varchar(10000)`.
- Migrations: `V1__Initial_schema.sql` declares `varchar(4000)`, and nothing in the fork changes it.
- The live width is intentional. Widening it was a local change to stop long frame lists failing the job launch.

Do not add a fork migration for this. A fork `V35` would collide with upstream's `V35` when the fork merges upstream. A migration with an out-of-order number would run on top of upstream's fix and be redundant.

Upstream already fixed it. `V48__increase_layer_range_size.sql` runs:

```sql
ALTER TABLE layer ALTER COLUMN str_range TYPE text;
ALTER TABLE layer ALTER COLUMN str_cmd TYPE text;
```

After the upstream merge, `flyway migrate` applies V35 to V51 from the baseline at 34. V48 turns the hand-widened column into `text`, which is wider than anything we set, so the live schema and the migrations agree again. After that upgrade the schema compare (`cuebot_schema/compare.sh`, in the pipeline team's sandbox) should show no `str_range` difference.

V48 also widens `layer.str_cmd`. Look at its live type before the upgrade. A `varchar` or `text` column converts cleanly. A narrower or different type than the migrations expect would be a second hand-made difference to record here.

## 2. Checklist for the upstream merge and upgrade

1. Merge upstream into the fork and check the fork-only patches (see `git log upstream/master..master`) still apply.
2. Back up the live database: `pg_dump -Fc cuebot_local > cuebot_local_<date>.dump`, then `pg_restore -l` the file to confirm it lists. Keep dumps somewhere that survives a reboot, not `/tmp`.
3. Restore that dump into a scratch database and run `flyway migrate` there first. This shows whether V35 to V51 apply cleanly on a schema that was loaded by hand. Fix surprises on the scratch copy, not on production.
4. Look at the things that were hand-loaded and could trip later migrations:
   - The V13 trigger functions (`trigger__after_insert_job`, `trigger__after_insert_layer`, `trigger__frame_history_open`) were recreated by `fix_live.sql`. A later migration that replaces them will simply overwrite them.
   - The triggers `update_frame_checkpoint_state` and `update_frame_wait_to_dep` have `WHEN` casts written differently on the live database. The logic is the same. A later migration that drops and recreates them will normalise this.
   - Grants: the `cuebot` role needs `USAGE` on every sequence it inserts through (it was missing on `layer_output_ser_order_seq`, which broke per-layer outputs, OP-1119). Check any new sequence a migration creates, because migrations run as the role that owns the objects.
5. Confirm V48's `ALTER` does not hold a long lock on `layer`. Changing `varchar` to `text` does not rewrite the table in PostgreSQL, so it should be quick, but check on the scratch copy with a realistic row count.
6. Stop Cuebot, run `flyway migrate` against production, start the matching Cuebot version, then run the schema compare and the end-to-end check from the pipeline (submit a job with an `<output>` and check a `layer_output` row appears).

## 3. Flyway rules for this database

- Production schema changes go through Flyway from the migrations in this repo. Never apply raw SQL by hand, because `flyway_schema_history` must stay the record of what was applied. The one exception so far is the guarded `DROP` described below.
- Never run `flyway clean`. It drops everything in the schema.
- Flyway 9.11.0 will not baseline into a schema whose `flyway_schema_history` table already exists, even when that table is empty (`Unable to baseline schema history table ... as it already exists, and is empty`). On odfarm01 the empty table was dropped inside a transaction that first checked it held no rows, and then `baseline -baselineVersion=34` succeeded. Expect the same if the history table is ever empty again.
- `flyway` is not installed on odfarm01 and the rez `cuebot` package does not contain it. The baseline was run from a container (`flyway/flyway:9.11.0`) over an SSH tunnel to the database. Close the tunnel afterwards: while it is open, anyone on the machine holding it has passwordless access to the database, because `pg_hba.conf` trusts TCP connections from localhost.
