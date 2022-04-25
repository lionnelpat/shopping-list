from smtplib import SMTPAuthenticationError

import requests
import sys
import time
import yagmail
import re

DISH_URL = "https://finelunch-api.herokuapp.com/api/v1/dishes"
TVA = 0.18
YAGMAIL_USERNAME = "dplionnel@gmail.com"
YAGMAIL_PASSWORD = "shmkgmyvvuocpgan"


def get_dishes(url):
    """
        get dishes from the remote server
    :param url: the server url
    :return: list of dishes as JSON format
    """
    res = requests.get(url)
    data = res.json()
    return data


def get_daily_menu(my_dishes):
    """
        get daily menu by taking the first five dishes on server
    :param my_dishes:  list of dishes comming from server
    :return: shorten list of dish for the day
    """
    menu = []
    for dish in my_dishes:
        if dish["dish_type"]["name"] == "African":
            menu.append(dish)

    return menu


def show_options():
    """
        Just print the program menu
    :return: None
    """
    print('''Bienvenue au restaurant du CESAG. Que souhaitez-vous faire? 

    1- Ajouter un plat à votre panier
    2- Supprimer un plat du panier
    3- Voir son panier (liste des plats ajoutés) 
    4- Vider son panier 
    5- Voir sa facture
    6- Passer la commande (quitter le programme)
    '''
    )


def show_daily_menu(daily_dishes):
    """
        show the daily menu
    :param daily_dishes: daily menu
    :return: None
    """
    print("Voici les plats du jour! ")
    for dish in daily_dishes:
        print(f"{daily_dishes.index(dish) + 1} - { dish['name']} ( {dish.get('price')} CFA)")


def get_and_validate_program_options():
    """
        get the program option from user
        validate it by check if it's a digit and between 1 and 6
    :return: valid option converted to int
    """
    opt = input("Quel est votre choix ? ")

    while not (opt.isdigit() and (int(opt) in range(1, 7))):
        print("Sasie incorrecte! le choix doit etre entre 1 et 6")
        opt = input("Quel est votre choix ? ")

    return int(opt)


def get_and_validate_menu_choice():
    """
        get menu choice number from user
        check if it's valid (digit and between 1 and 5)

    :return: choice converted to integer
    """
    choice = input("Entrez le numéro du plat correspondant ")

    while not (choice.isdigit() and (int(choice) in range(1, 6))):
        print("Saisie incorrecte, merci de saisir un chiffre entre 1 et 5 ")
        choice = input("Entrez le numéro du plat correspondant ")

    return int(choice)


def get_and_dish_quantity():
    """
        get dish quantity and check if it's valid
    :return: quantity converted to int
    """
    qte = input("Entrez la quantité: ")
    while not qte.isdigit():
        print("La quantité doit etre une valeur numérique")
        qte = input("Entrez la quantité: ")

    return int(qte)


def get_index_of_dish_to_delete():
    """
        get number of dish to delete
        check if this number is valid
    :return: dish number converted to int
    """
    dish_index = input("Entrez le numéro du plat à supprimer ")
    while not (dish_index.isdigit() and int(dish_index) in range(1, len(user_cart)+1)):
        print("Entrée incorrecte!!!! ")
        dish_index = input("Entrez le numéro du plat à supprimer ")

    return int(dish_index)


def add_to_cart():
    """
        show daily menu
        get the number of dish to add and the quantity
        save dish to cart if not exist or just update the quantity
    :return: None
    """
    show_daily_menu(MENU_OF_DAY)
    choice_option = get_and_validate_menu_choice()
    qte = get_and_dish_quantity()
    selected_dish = MENU_OF_DAY[choice_option-1]

    if len(user_cart) == 0:
        selected_dish["quantity"] = int(qte)
        user_cart.append(selected_dish)
    else:
        for dish in user_cart:
            if dish['id'] == selected_dish['id']:
                print(f" quantité présente {selected_dish['quantity'] }")
                print(f" quantité à ajouter {qte} ")
                selected_dish['quantity'] += int(qte)
                break
        else:
            selected_dish["quantity"] = int(qte)
            user_cart.append(selected_dish)

    print("Plat ajouté avec success")
    time.sleep(1)


def remove_from_cart():
    """
        ask the number of dish to remove  and remove it from cart
        print empty cart if cart is empty
    :return: None
    """
    if len(user_cart) == 0:
        print("Le panier est vide!!!")
    else:
        show_cart()
        dish_index = get_index_of_dish_to_delete()
        user_cart.pop(dish_index-1)

    print("Plat retiré avec success")
    time.sleep(1)


def show_cart():
    """
        list all dish in cart with quantity
    :return: None
    """
    if len(user_cart) == 0:
        print("\nVotre Panier est vide")
    else:
        for dish in user_cart:
            print(f"{user_cart.index(dish) + 1} - { dish.get('name')} ({ dish.get('quantity')})")
    time.sleep(1)


def delete_cart():
    """
        delete all dishes in cart
    :return: None
    """
    if len(user_cart) == 0:
        print("\nLe panier est vide !!!")
    else:
        user_cart.clear()
        print("\nPanier vidé avec succès!!!")

    time.sleep(1)


def show_bill():
    """
        show all dishes in cart
        show total of amount, TVA and TTC
    :return: None
    """
    if len(user_cart) != 0:
        montant = 0.0
        for dish in user_cart:
            montant += (dish.get('quantity') * dish.get('price'))
            print(f"{user_cart.index(dish) + 1} - {dish.get('name')} ({dish.get('quantity')})")

        tva = float(montant) * TVA
        total = montant + tva
        print("\n")
        print(f"Montant HT: { montant }")
        print(f"Montant TVA: { round(tva) }")
        print(f"Montant TTC: { total }")


def is_email_valid(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.fullmatch(regex, email):
        return True
    else:
        return False


def send_email():
    yagmail.register(YAGMAIL_USERNAME, YAGMAIL_PASSWORD)
    user_email = input("Enter Email to send bill ")

    while not is_email_valid(user_email.strip().lower()):
        user_email = input("Enter Email to send bill ")

    try:
        yag = yagmail.SMTP(YAGMAIL_USERNAME)
        body = f"""
                Bonjour Vous avez une nouvelle facture!
                Votre commande sera livrée dans les plus brefs delais 
                Merci pour votre confiance
                """
        yag.send(
            to=user_email,
            subject="Shopy Food | Votre commande a bien été reçu !",
            contents=body
        )
        print("Votre commande a bien été passée! \n Merci pour votre confiance \n A bientot")
    except SMTPAuthenticationError as e:
        print(e)


def quit_program():

    if len(user_cart) != 0:
        send_email()

    sys.exit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    user_cart = []
    option = ""
    dishes = get_dishes(DISH_URL)
    MENU_OF_DAY = get_daily_menu(dishes)

    while option != 6:
        print("\n")
        show_options()
        user_option = get_and_validate_program_options()
        print("\n")
        if user_option == 1:
            add_to_cart()
        elif user_option == 2:
            remove_from_cart()
        elif user_option == 3:
            show_cart()
        elif user_option == 4:
            delete_cart()
        elif user_option == 5:
            show_bill()
        else:
            quit_program()
