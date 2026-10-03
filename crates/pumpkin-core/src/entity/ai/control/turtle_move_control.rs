use crate::entity::{
    ai::control::{Control, MoveControlTrait, move_control::MoveControl},
    mob::Mob,
};
use std::sync::atomic::Ordering;

#[derive(Default)]
pub struct TurtleMoveControl {
    land: MoveControl,
}

impl Control for TurtleMoveControl {}

impl MoveControlTrait for TurtleMoveControl {
    fn tick(&mut self, mob: &dyn Mob) {
        let entity = mob.get_entity();
        if entity.touching_water.load(Ordering::Relaxed) {
            // TurtleMoveControl.updateSpeed balances the idle sink in water travel.
            let mut velocity = entity.velocity.load();
            velocity.y += 0.005;
            entity.velocity.store(velocity);
        } else {
            self.land.tick(mob);
        }
    }
}
