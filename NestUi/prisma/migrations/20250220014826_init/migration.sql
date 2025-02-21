-- CreateTable
CREATE TABLE "Buoy" (
    "buoy_id" SERIAL NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "long" DOUBLE PRECISION NOT NULL,
    "battery" INTEGER NOT NULL,
    "drop_time" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Buoy_pkey" PRIMARY KEY ("buoy_id")
);
