def write_cmd(cmd, file_name):
    try:
        with open(file_name, "w") as dev:
            dev.write(cmd)

    except Exception as e:
        print(f"Общая ошибка: {e}")
        
    finally:
        return
    
def read_cmd(file_name):
    res = ""
    try:
        with open(file_name, "r") as dev:
            while True:
                symb = dev.read(1)
                if symb == '\n':
                    break
                res += symb

    except Exception as e:
        print(f"Общая ошибка: {e}")

    finally:
        return res
    
