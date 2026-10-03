# Pumpkin fork maintenance

Fork: https://github.com/mateo-cogeanu/Pumpkin
Upstream: https://github.com/Pumpkin-MC/Pumpkin (`origin/master`)
Maintenance branch: `fix/floating-trees-and-aquatic-mobs`
Upstream baseline: `1859221e7ad1227f43277f74507f921c0acec83f`
Schedule: daily at 09:00 Europe/Prague, in this Codex chat (`maintain-pumpkin-fixes`).
The automation prepares validated local updates; it does not deploy or push.

## Patch commits

- `e58626324`: tree provider resolution and regression.
- `97e5179f8`: aquatic travel/navigation and control integration.

## Patches

1. **Tree ground.** Resolve named block-state providers from the bundled vanilla
   datapack in codegen. Previously `minecraft:soil_beneath_tree` became AIR, so
   trunk placement removed the block beneath a tree. Regenerate configured
   features through codegen. Grass becomes dirt where vanilla specifies dirt;
   existing solid dirt/moss remains solid. This affects newly placed trees and
   new generation. It does not repair gaps already saved in existing worlds.
2. **Aquatic movement.** Fish and squid changes adapt the implementation in
   upstream PR https://github.com/Pumpkin-MC/Pumpkin/pull/3718 (still open when
   adopted). Water navigation, swimming targets and species-specific travel
   replace land navigation and the surface-jump goal. Extend the correction to
   dolphin, axolotl, tadpole, guardian, elder guardian, nautilus and turtle.
   Axolotls and turtles retain amphibious navigation. Wire smooth control to
   waypoints and effective speed; follow underwater waypoints at feet height
   with vanilla tolerances. Normal land mobs retain their float goal.

References: vanilla Java server 26.3, bundled provider JSON and tags;
`AbstractFish`, `Squid`, `SmoothSwimmingMoveControl`, `PathNavigation`,
`WaterBoundPathNavigation`, `AmphibiousPathNavigation`, `AbstractNautilus`,
`Turtle`. Also watch upstream aquatic issue #3468 and PR #3649.

## Update procedure

- Read root and applicable crate AGENTS.md. Preserve user edits and worlds.
- Fetch `origin/master`. If unchanged and nothing actionable changed, stay quiet.
- Use an isolated checkout of **unpatched new upstream**. Check each bug
  independently before carrying any local patch forward. Inspect implementation
  and run the regression/probe; a commit title or clean cherry-pick proves nothing.
- Tree regression: transplant only
  `tree_soil_provider_preserves_ground_beneath_trunks` into upstream if absent;
  run `cargo test --locked -p pumpkin-world tree_soil_provider_preserves`.
- Aquatic scratch probe is kept outside the repository at
  `/Users/mateocogeanu/Documents/Projects/bostanmc/.pumpkin-checks/aquatic-test.rs`.
  Temporarily append it to core `entity/living.rs` in the isolated checkout,
  run `cargo test --locked -p pumpkin-core aquatic_mobs_can_dive -- --nocapture`,
  then restore that file. The probe creates a loaded water chunk, exercises actual
  AI to detect surface jumping, then actual navigation/control/travel to verify
  horizontal swimming and descent across eleven supported aquatic types, plus AI and directed-velocity travel
  checks for squid and glow squid.
  Adapt it to upstream APIs as needed; never commit the scratch module.
- Omit patches for bugs upstream has actually fixed. Adapt only still-needed
  fixes on a new integration branch. Avoid applying overlapping PR changes twice.
- Regenerate data if required, run fmt, affected-crate/dependent clippy and tests,
  the existing worldgen feature benchmark against the unpatched baseline, and a
  scratch server boot. Advance maintenance branch only after checks pass.
- Update baseline, patch commits, evidence and limitations here. For unresolved
  conflicts or failures, preserve the last working branch and report the cause.
- Notify for meaningful validated updates, removal of redundant patches,
  failures or required user action. Remote pushes need user authorization.
  Never deploy, overwrite user edits, change saved worlds, force-push, create PRs
  or post GitHub comments automatically.

## Local toolchain and checks

This checkout requires Rust >=1.96. The Homebrew default was 1.95; validation uses
rustup stable 1.99. Add
`/Users/mateocogeanu/.rustup/toolchains/stable-aarch64-apple-darwin/bin` to PATH.
Set `CARGO_PROFILE_DEV_STRIP=none` for debug checks on this Mac.
Keep validation logs and vanilla sources in the sibling `.pumpkin-checks` directory.

Validation on 2026-10-03:

- Unpatched baseline: tree regression FAIL (AIR instead of DIRT); aquatic probe
  FAIL (`cod is surface jumping`). Patched: tree regression PASS; thirteen-type
  aquatic probe PASS (eleven navigation types plus squid/glow-squid travel).
- `cargo nextest run --locked --workspace --no-tests=pass --test-threads=4`:
  1102 passed, zero skipped. Includes existing vanilla world-generation fixtures.
- `cargo fmt --check`, `git diff --check`, `cargo-machete`, `typos`: PASS.
- Existing Criterion `features_generation`, same seed/machine, two runs each,
  dev profile, 30 samples, 2s warm-up, 10s requested measurement:
  upstream central estimates 4.9741ms / 4.7148ms;
  patched 4.7530ms / 5.0370ms. Intervals overlap between runs; these debug results
  do not establish a meaningful performance change or release-build throughput.
- `cargo clippy --locked -p pumpkin -p pumpkin-core -p pumpkin-world -p
  pumpkin-data -p pumpkin-codegen --all-targets --all-features -- -D warnings`:
  PASS. Existing dependency future-compatibility warning: `proc-macro-error2
  2.0.1`.
- `cargo build --locked -p pumpkin`: PASS. macOS debug linker emits its
  existing large `__eh_frame` warning; no new code warnings.
- Rebuilt scratch server: `Started server; took 596ms`; console `version` then
  `stop`; saved and shut down with exit 0. No errors or panics. Only normal
  debug/development/non-TTY warnings. The initial wrapper inherited
  `RUST_LOG=warn` and left stdin open; corrected to INFO and closed stdin before
  waiting. The successful repeat is `.pumpkin-checks/boot-final.log`.
- Latest upstream fetched again: baseline unchanged; PR #3718 still open.
- Mineflayer upstream documents support through 26.1, not this checkout's 26.3:
  https://github.com/PrismarineJS/mineflayer . No real-client bot play test claimed.

## Gameplay limits and human check

The probe is an in-process physics/AI check, not a real client play test. It forces
submersion while ticking; it does not verify rendering, animations, sounds or
natural spawning. Advanced existing AI gaps (schooling, dolphin breathing and
quests, guardian attacks, axolotl brain and turtle home/egg behavior) remain.
Zombie nautilus has no dedicated entity implementation in this baseline.
Nautilus can rise while idle, as vanilla does; it must still be able to dive.

Before using this build on a saved world, join a scratch world with a matching
26.3 client and do these checks:

- Generate new forest chunks and grow saplings: expect solid dirt/allowed soil
  beneath trunks. Capture the trunk base and the block below it.
- In a deep water tank summon cod, salmon, tropical fish, pufferfish, squid,
  glow squid, dolphin, axolotl, tadpole, guardian, elder guardian, nautilus and
  turtle: expect swimming at depth without persistent surface jumping. Record
  movement for at least a minute, including a dive and direction change.
- Strand a fish: expect flopping. Move an axolotl/turtle between water and land:
  expect both terrain types to remain usable. Put a normal land mob in water:
  expect its survival float behavior to remain.

Console-only world commands could not exercise loaded chunks without a player
on this baseline. Do not report console command success as a gameplay pass.
If contributing upstream, a human must play test, attach these captures, and open
separate PRs for the tree and aquatic changes using the prepared descriptions.
