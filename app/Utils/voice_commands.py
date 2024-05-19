import rapidfuzz
from unidecode import unidecode

command_dict = {
    "off bedroom": "tat phong ngu",
    "on bedroom": "mo phong ngu",
    "off livingroom": "tat phong khach",
    "on livingroom": "mo phong khach",
    "off kitchen": "tat bep",
    "on kitchen": "mo bep",
    "latest temp": "nhiet do",
    "latest moist": "do am",
}


def get_command(query_string: str, choices=command_dict, cutoff=50):
    a = rapidfuzz.process.extractOne(
        query=unidecode(query_string),
        choices=choices,
        scorer=rapidfuzz.fuzz.partial_token_sort_ratio,
        score_cutoff=cutoff,
    )
    if not a:
        return None
    return a[2]


if __name__ == "__main__":
    query_string = "tắt đèn hồn phách "
    print(get_command(query_string))
