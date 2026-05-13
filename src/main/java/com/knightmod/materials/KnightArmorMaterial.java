package com.knightmod.materials;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;

public final class KnightArmorMaterial implements ArmorMaterial {

    public static final KnightArmorMaterial INSTANCE = new KnightArmorMaterial();

    private static final int[] DURABILITY_BY_SLOT = new int[]{
            2000,  // FEET
            3200,  // LEGS
            4096,  // CHEST
            1512   // HEAD
    };

    private static final int[] DEFENSE_BY_SLOT = new int[]{
            5,     // FEET
            12,    // LEGS
            15,    // CHEST
            7      // HEAD
    };

    private KnightArmorMaterial() {}

    @Override
    public int getDurabilityForSlot(EquipmentSlot slot) {
        return DURABILITY_BY_SLOT[slot.getIndex()];
    }

    @Override
    public int getDefenseForSlot(EquipmentSlot slot) {
        return DEFENSE_BY_SLOT[slot.getIndex()];
    }

    @Override
    public int getEnchantmentValue() {
        return 15;
    }

    @Override
    public SoundEvent getEquipSound() {
        return SoundEvents.ARMOR_EQUIP_IRON;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(Items.IRON_INGOT);
    }

    @Override
    public String getName() {
        return "knightmod:knight";
    }

    @Override
    public float getToughness() {
        return 3.0F;
    }

    @Override
    public float getKnockbackResistance() {
        return 0.1F;
    }
}
