# Procedural motion toolbox

For games with unusual movement (multi-legged creatures, arms that grab/climb, wall walking,
ragdoll-ish characters). Pick the few techniques the reference actually shows; don't stack them all.

## Diagnose first (from the reference)
- Do limbs plant and stay fixed while the body moves? → procedural stepping + IK.
- Does the body tilt to match walls/ceilings? → surface normal alignment.
- Does the body bob/lean with steps or speed? → body stabilisation from foot average.
- Do limbs swing with physics, react to hits? → physics-based animation (springs/joints).
- Otherwise clip animation + blend tree is cheaper and usually looks better.

## Techniques
- **Raycasting for ground/surface**: per foot, cast from a hip-relative "home" point along -bodyUp
  (and forward for climbing). Store hit point + normal. Cap length; handle misses (dangle/reach).
- **Procedural stepping**: each foot keeps a planted world position. When distance(planted, desired)
  > stepThreshold (scaled by speed) and the foot's group partner is planted, start a step: lerp to the
  predicted target (desired + velocity * stepDuration * 0.5) with an arc (sin(t·π)·height). Alternate
  groups (tripod gait for 6 legs, diagonal pairs for 4). Clamp max simultaneous steps.
- **IK**: 2-bone analytic IK (law of cosines + pole vector) for most legs/arms; FABRIK or CCD for 3+
  bones/tentacles. Solve after physics/locomotion, before render. Respect joint limits.
- **Foot placement**: align foot to the hit normal; blend IK weight to 0 in air.
- **Body stabilisation**: body height = average planted feet height + offset; body tilt from the
  plane fitted to feet; smooth with critically damped springs (frame-rate independent).
- **Surface normal alignment**: smoothed up-vector = slerp(currentUp, averageNormal, 1-exp(-k·dt));
  rebuild orientation from up + projected forward; gravity along -up for wall walkers.
- **Physics-based animation**: drive joints with PD controllers/springs toward target pose; or
  spring-damper secondary motion for antennae, tails, cloth-like parts.

## Engine notes
- PlayCanvas: do IK in a script's `postUpdate` on the skeleton's entities after the anim component
  updates; raycasts via `app.systems.rigidbody.raycastFirst` (needs Ammo). Check `reuse-scripts`
  for anything the engine already ships.
- Three.js: `CCDIKSolver` exists in examples/jsm; for 2-bone IK write the analytic solver.
  Raycast with Rapier (`castRay`) or `THREE.Raycaster` against simplified collision meshes.

## Verify
Debug draw: home points, ray hits, normals, step targets, IK targets. Record a short Playwright video
or frame sequence and compare to the reference burst frames (game-reference-analysis `burst`).
