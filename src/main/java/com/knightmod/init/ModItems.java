package com.knightmod.init;

import com.knightmod.KnightMod;
import com.knightmod.items.KnightDaggerItem;
import com.knightmod.materials.KnightArmorMaterial;
import com.knightmod.materials.KnightToolTier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SwordItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, KnightMod.MOD_ID);

    private static final CreativeModeTab TAB = CreativeModeTab.TAB_COMBAT;

    public static final RegistryObject<Item> KNIGHT_HELMET = ITEMS.register(
            "knight_helmet",
            () -> new ArmorItem(KnightArmorMaterial.INSTANCE, EquipmentSlot.HEAD,
                    new Item.Properties().tab(TAB)));

    public static final RegistryObject<Item> KNIGHT_CHESTPLATE = ITEMS.register(
            "knight_chestplate",
            () -> new ArmorItem(KnightArmorMaterial.INSTANCE, EquipmentSlot.CHEST,
                    new Item.Properties().tab(TAB)));

    public static final RegistryObject<Item> KNIGHT_LEGGINGS = ITEMS.register(
            "knight_leggings",
            () -> new ArmorItem(KnightArmorMaterial.INSTANCE, EquipmentSlot.LEGS,
                    new Item.Properties().tab(TAB)));

    public static final RegistryObject<Item> KNIGHT_BOOTS = ITEMS.register(
            "knight_boots",
            () -> new ArmorItem(KnightArmorMaterial.INSTANCE, EquipmentSlot.FEET,
                    new Item.Properties().tab(TAB)));

    public static final RegistryObject<Item> KNIGHT_SWORD = ITEMS.register(
            "knight_sword",
            () -> new SwordItem(KnightToolTier.SWORD, 19, -2.4F,
                    new Item.Properties().tab(TAB)));

    public static final RegistryObject<Item> KNIGHT_DAGGER = ITEMS.register(
            "knight_dagger",
            () -> new KnightDaggerItem(KnightToolTier.DAGGER, 8, -1.0F,
                    new Item.Properties().tab(TAB)));

    private ModItems() {}
}
