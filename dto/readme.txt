Device tree overlays for the YRL028
Device tree overlays

The Device Tree Source (DTS) file for the target board revision must first be compiled into Device Tree Blob (DTB) overlays as follows:

dtc -@ -I dts -O dtb -o yrl028-led.dtbo yrl028-led.dts

The resulting .dtbo file should then be copied to /boot/overlays/ on the Raspberry Pi. To enable the overlay, add the following line to /boot/config.txt, using the correct board revision number, and replacing the parameters as detailed below:

dtoverlay=yrl028-led
