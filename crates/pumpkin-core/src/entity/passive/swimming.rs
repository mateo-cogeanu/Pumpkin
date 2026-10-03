use std::sync::atomic::Ordering;

use crate::entity::{EntityBase, mob::Mob};

/// Water travel shared by dolphins, axolotls, nautiluses and guardians.
/// Each caller supplies its vanilla acceleration and idle sinking condition.
pub fn travel(mob: &dyn Mob, caller: &dyn EntityBase, speed: f64, sink: bool) -> bool {
    let living = &mob.get_mob_entity().living_entity;
    let entity = &living.entity;
    if !entity.touching_water.load(Ordering::Relaxed) {
        return false;
    }
    entity.update_velocity_from_input(living.movement_input.load(), speed);
    living.make_move(caller);
    let mut velocity = entity.velocity.load() * 0.9;
    if sink {
        velocity.y -= 0.005;
    }
    entity.velocity.store(velocity);
    true
}
