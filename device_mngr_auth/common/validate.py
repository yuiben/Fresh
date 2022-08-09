
special_character = "~!@#$%^&*()_+=-.,/?\|{}[];:'\""

number = "0123456789"

character = "abcdefghijklmnopqrstuvwxyz"
    
def check_character(character):
    char = 0
    num = 0
    special = 0
    
    for value in character:
        if char == 0 or num == 0 or special == 0:
            if char == 0:
                if value in character:
                    char += 1
                    continue
            if num == 0:
                if value in number:
                    num += 1
                    continue
            if special == 0:
                if value in special_character:
                    special += 1
                    continue
        else:
            break
    if char == 0:
        return "Password must contain alphanumeric characters !"
    elif num == 0:
        return "Password must have numeric characters !"
    elif special == 0:
        return "Password must have special characters !"
    else:
        return ""
    
def check_form_password_user(password):
    if password.islower():
        return "Password must have uppercase characters"
    return check_character(set(password.lower()))

