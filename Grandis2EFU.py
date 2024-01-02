import datetime, time, zipfile
from urllib.request import urlopen
from io import BytesIO

zip_url = "http://ftp2.grandis.nu/turran/FTP/filelist.zip"
path_prefix = "X:\\"
timestamp_type = 1
progress_width = 50
step = 12024

def wait_exit():
    print("\nNaciśnij dowolny klawisz, aby zakończyć.")
    input()
    exit()


def download():
    with urlopen(zip_url) as response:
        with zipfile.ZipFile(BytesIO(response.read())) as zip_file:
            file_list = zip_file.namelist()
            if len(file_list) == 1 and file_list[0].endswith(".txt"):
                try:
                    return zip_file.read(file_list[0]).decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    print("Błąd dekodowania pliku. Spróbuj innego kodowania.")
                    wait_exit()
            else:
                print("Nieprawidłowy format pliku ZIP lub brak pliku TXT wewnątrz.")
                wait_exit()


def convert(files):
    data = []
    wiersze_dp = len(files)
    i2 = 0

    def progress_update():
        progress = int(progress_width * index / wiersze_dp) # Aktualizacja paska postępu w trybie tekstowym
        bar = "[" + "#" * progress + " " * (progress_width - progress) + "]"
        print(f"\r{bar} {index}/{wiersze_dp}", end="", flush=True)

    for index, file_info in enumerate(files, start=1):
        file_data = file_info.split("|")
        date_time = datetime.datetime.strptime(file_data[0], "%Y-%m-%dT%H:%M:%S%z")
        unix_timestamp = str(int(date_time.timestamp() * 100))
        #unix_timestamp = str(int(time.mktime(time.strptime(file_data[0], "%Y-%m-%dT%H:%M:%S%z"))) * 100)
        size = file_data[1]
        filename = file_data[2].replace('/', '\\')
        row = f'"{path_prefix}{filename}",{size},{unix_timestamp},,0' # Składanie wiersza
        data.append(row)
        if index > i2:
            progress_update()
            i2 = index + step
    progress_update()
    return data


def main():
    timestamp1 = int(time.time())
    timestamp2 = time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp1))
    if timestamp_type > 1: timestamp1 = timestamp2
    output_file = "grandis-nu_" + str(timestamp1) + ".efu"
    header = "Filename,Size,Date Modified,Date Created,Attributes"
    

    print("Konwersja listy plików z serwera grandis.nu na listę plików Everything (EFU).\n")
    print("Pobieranie pliku z", zip_url)
    file_content = download()

    files = file_content.strip().split("\n") # Podział linii na listę
    
    print("Procesowanie wierszy...")
    data = convert(files)

    print("\nZapisywanie...")
    with open(output_file, mode="w", encoding="utf-8") as text_file:
        text_file.write(header + "\n")
        text_file.write("\n".join(data))

    print("Dane zostały zapisane w pliku ", output_file)
    wait_exit()

if __name__ == "__main__":
    main()