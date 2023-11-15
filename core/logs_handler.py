import os


def write_log_file(message):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(base_dir, '../logs')
    with open(f'{files_dir}/trade_logs.txt', 'w', encoding='utf-8') as file:
        file.write(str(message))


def read_logs_txt():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(base_dir, '../logs')

    with open(f'{files_dir}/trade_logs.txt', 'r', encoding='utf-8') as file:
        join_text = [line for line in file]
        print(join_text)
    return join_text


if __name__ == '__main__':
    mes = 'hello'
    write_log_file(mes)
