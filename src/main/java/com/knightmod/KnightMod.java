package com.knightmod;

import com.knightmod.init.ModItems;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

@Mod(KnightMod.MOD_ID)
public class KnightMod {

    public static final String MOD_ID = "knightmod";
    private static final Logger LOGGER = LogUtils.getLogger();

    public KnightMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        ModItems.ITEMS.register(modEventBus);

        LOGGER.info("Knight Mod loaded");
    }
}
