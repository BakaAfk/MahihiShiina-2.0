import re

def extract_and_decode_hex(text):
    results = []
    matches = re.findall(r'(?:[0-9a-fA-F]{2}\s*)+', text)

    for m in matches:
        hex_str = m.replace(" ", "")
        try:
            decoded = bytes.fromhex(hex_str).decode("utf-8")
            results.append(decoded)
        except ValueError:
            pass
        except UnicodeDecodeError:
            pass

    return results


text = input("Nhap string cua ban: ")
decoded_results = extract_and_decode_hex(text)

for res in decoded_results:
    print(res)
