import random
import re
import string


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.hexdigits, k=length))


def get_unique_id(length: int) -> str:
    return "".join(
        random.choices(
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-",
            k=length,
        )
    )


def get_client_ip(request):
    if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        return x_forwarded_for.split(",")[0].strip()
    else:
        return request.META.get("REMOTE_ADDR")


def check_unclosed_tags(html_text):
    tag_pattern = r"<[^>]*>"
    tags = re.findall(tag_pattern, html_text)
    print("tags", tags)
    if not tags:
        return True

    stack = []

    for tag in tags:
        if tag == "<br>":
            continue
        # exception for <img src="">
        if "<img" in tag:
            continue
        if "</" not in tag:
            tag = tag.split(" ")[0]
            if tag[-1] != ">":
                tag += ">"
            print("MODIFIED", tag)
            stack.append(tag)
            print("appended", stack)
        else:
            if not stack:
                return False
            print(">>", tag[2:-1], stack[-1][1:-1])
            if tag[2:-1] != stack[-1][1:-1]:
                return False
            stack.pop()

    if stack:
        return False
    return True
