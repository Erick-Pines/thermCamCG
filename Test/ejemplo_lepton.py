# LEPTON: Obtener la temperatura de un objeto.
#
# Muestra la temperatura de un objeto basado en su color.

# By turning the AGC off and setting a max and min temperature range you can make the lepton into
# a great sensor for seeing objects of a particular temperature. That said, the FLIR lepton is a
# microblobometer and not a thermophile. So, it needs to re-calibrate itself often (which is called
# flat-field-correction - FFC). Additionally, microblobmeter devices require pprocessing support
# onboard to deal with the effects of temperature drift which is called radiometry support.

# FLIR Lepton Shutter Note: FLIR Leptons with radiometry and a shutter will pause the video often
# as they heatup to re-calibrate. This will happen less and less often as the sensor temperature
# stablizes. You can force the re-calibration to not happen if you need to via the lepton API.
# However, it is not recommended because the image will degrade overtime.

#IMPORTANTE:

# Si usamos un LEPTON dirente al 3.5, puede que este script no funcione a la perfección, ya que otros
# leptons no cuentan con soporte para radiometría o no activan su proceso de calibración con la
# con la suficiente frecuencia para lidiar con el cambio de temperatura (FLIR 2.5).
import sensor, image, time, math

# Umbrales para seguir color en Escala de Grises (Grayscale Min, Grayscale Max)
threshold_list = [(200, 255)]

# Rangos de temperatura:
min_temp_in_celsius = 20.0
max_temp_in_celsius = 35.0

print("Resetting Lepton...")
# Configuraciones que se aplican al reiniciar:
sensor.reset()
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_MODE, True)
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_RANGE, min_temp_in_celsius, max_temp_in_celsius)
print("Lepton Res (%dx%d)" % (sensor.ioctl(sensor.IOCTL_LEPTON_GET_WIDTH),
                              sensor.ioctl(sensor.IOCTL_LEPTON_GET_HEIGHT)))
print("Radiometry Available: " + ("Yes" if sensor.ioctl(sensor.IOCTL_LEPTON_GET_RADIOMETRY) else "No"))

sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=5000)
clock = time.clock()

#IMPORTANTE:

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" merges all overlapping blobs in the image.

def map_g_to_temp(g):
    return ((g * (max_temp_in_celsius - min_temp_in_celsius)) / 255.0) + min_temp_in_celsius

while(True):
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs(threshold_list, pixels_threshold=200, area_threshold=200, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        stats = img.get_statistics(thresholds=threshold_list, roi=blob.rect())
        img.draw_string(blob.x(), blob.y() - 10, "%.2f C" % map_g_to_temp(stats.mean()), mono_space=False)
    print("FPS %f - Lepton Temp: %f C" % (clock.fps(), sensor.ioctl(sensor.IOCTL_LEPTON_GET_FPA_TEMPERATURE)))
