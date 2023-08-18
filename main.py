import sys, os

from garmin_fit_sdk import Decoder, Stream, Profile


MESSAGES = [
    # "FILE_ID",
    # "FILE_CREATOR",
    # "EVENT",
    # "DEVICE_INFO",
    # "DEVICE_AUX_BATTERY_INFO",
    # "DEVICE_SETTINGS",
    # "USER_PROFILE",
    # "SPORT",
    # "ZONES_TARGET",
    # "TRAINING_FILE",
    # "WORKOUT",
    # "WORKOUT_STEP",
    # "RECORD",
    # "GPS_METADATA",
    # "LAP",
    # "SET",
    # "LENGHT",
    # "TIME_IN_ZONE",
    # "SPLIT",
    # "SESSION",
    # "ACTIVITY",

    # "MONITORING_INFO",
    # "MONITORING",
    # "MONITORING_HR_DATA",
    # "STRESS_LEVEL",
    # "RESPIRATION_RATE",

    "SLEEP",
    "SLEEP_ASSESSMENT"
]

root_path: str = "assets/fenix6s_all_files_after_garmin_connect_descon"
messages = []


def mesg_listener(mesg_num: int, mesg: dict) -> None:
    for name, num in Profile["mesg_num"].items():
        # if mesg_num == num:
        #     print(name)
        #     print(mesg)
        # if name in MESSAGES and mesg_num == num  and "timestamp" in mesg  and mesg["timestamp"].year == 2023 and mesg["timestamp"].month == 9 and mesg["timestamp"].day == 26:
        # if mesg_num == num:
        if "sleep" in name.lower() and mesg_num == num:
            print(f"----- {name} - START")
            print(f"{repr(mesg)}")
            print(f"----- {name} -   END")
            print()


for dirpath, dirnames, filenames in os.walk(root_path):
    for filename in filenames:
        if filename.lower().endswith(".fit"):
            fit_file_path: str = os.path.join(dirpath, filename)

            stream = Stream.from_file(fit_file_path)
            decoder = Decoder(stream)
            messages, errors = decoder.read(mesg_listener=mesg_listener)

            ## print()
            ## print()
            ## print(f"FIT FILE PARSED: {fit_file_path}")
            ## input("Enter to continue...")
            ## print()

            ## for msg in messages:
            ##     print(msg)


# Los pasos que doy al día se guardan en la carpeta "Monitor" del reloj.
# Creo que hay un fichero por día pero se borra al sincronizar con Garmin
# Connect porque solo veo un fichero cada día que cambia de nombre.
#
# He podido comprobar que en ese fichero se tienen estos mensajes útiles:
# "MONITORING_INFO"
# "MONITORING"
# "MONITORING_HR_DATA"
# "STRESS_LEVEL"
# "RESPIRATION_RATE"
#
# !Cuidado!, porque en MONITORING tengo los "steps" pero lo veo duplicado
# en dos mensajes con el mismo contenido pero con una diferencia de 3 o 4
# minutos. Imagino que vendrá precedido de un MONITORING_INFO que aclare
# esto, porque parece que hay uno de los dos MONITORING que viene precedido
# por un MONITORING_INFO con el mismo timestamp. El otro MONITORING, unos
# minutos más tarde no parece venir detrás de un MONITORING_INFO.
