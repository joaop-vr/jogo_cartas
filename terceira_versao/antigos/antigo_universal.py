import socket
import json
import sys
import random

# Configurações da rede
TABLE_CARD = 0
ROUND = 0
TOKEN = False
IS_DEALER = False
DEALER_ID = 0
CARDS = []
MY_LIST = []
MY_CARDS = []
GUESSES = [None, None, None, None]
MOVES = [None, None, None, None]
COUNT_MOVES = [0, 0, 0, 0]
PLAYERS_IPS = ["10.254.223.39", "10.254.223.40", "10.254.223.41", "10.254.223.42"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
MY_ID = 0
MY_IP = 0
MY_PORT = 0
NEXT_ID = 0
NEXT_IP = 0
NEXT_PORT = 0

# Função de inicialização do jogo
def init_game(sock):
    global TOKEN, CARDS, MY_LIST, IS_DEALER, ROUND, TABLE_CARD

    # O carteador é o primeiro a receber um token
    TOKEN = True

    # Contador de rodadas
    ROUND = ROUND + 1

    # Distribui as cartas para os jogadores e armazena em 'cards'
    CARDS = distribute_cards()

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Prepara as mensagens de distribuição de cartas
    for i in range(1, 4):
        msg = {
            "type": "init",
            "from_player": MY_ID,
            "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
            "data": CARDS[i]
        }
        MY_LIST.append(msg)

    # Guardando as cartas do carteador
    global MY_CARDS
    MY_CARDS = CARDS.pop(0)
    TABLE_CARD = MY_CARDS.pop()
    print(f"Manilha: {TABLE_CARD}")
    print(f"Cartas do carteador: {MY_CARDS}")

    # Prepara as mensagens de solicitação de palpites
    for i in range(1,4):
        msg = {
            "type": "take_guesses",
            "from_player": MY_ID,
            "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
            "data": []
        }
        MY_LIST.append(msg)
    #msg = {
    #    "type":"take_guesses",
    #    "from_player": MY_ID,
    #    "to_player": MY_ID,
    #    "data": []
    #}
    #MY_LIST.append(msg)

    # Envia a primeira mensagem da lista
    msg = MY_LIST.pop(0)
    send_message(sock, msg, NEXT_IP, NEXT_PORT)

# Função fictícia para distribuir cartas
def distribute_cards():
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['A', '2', '3', '4', '5', '6', '7', 'J', 'Q', 'K']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    for i in range(ROUND):  # ROUND == número de cartas sorteadas
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())

    # Sorteando a manilha (table_card)
    random.shuffle(values)
    table_card = values.pop()
    for i in range(4):
        players_cards[i].append(table_card)
    return players_cards

# Função para o usuário informar o palpite
def take_guess(count_guesses=0):
    # Solicita o palpite do usuário
    while True:
        try:
            guess = int(input("Informe o seu palpite: "))
            if guess < 0:
                raise ValueError("O palpite deve ser um inteiro natural (não negativo).")
            break
        except ValueError as e:
            print(f"Entrada inválida: {e}. Tente novamente.")

    # Verifica se o palpite é maior que o número de cartas que possui
    while guess > len(MY_CARDS):
        print("Não é possível dar um palpite maior que o número de cartas que possui.")
        guess = int(input("Dê outro palpite: "))

    # Verifica se a soma dos palpites é igual ao número de rodadas
    if count_guesses != 0 and ROUND >= 2:
        while count_guesses + guess == ROUND:
            print(f"A soma dos palpites deve ser diferente de {ROUND}.")
            guess = int(input("Dê outro palpite: "))
            while guess > len(MY_CARDS):
                print("Não é possível dar um palpite maior que o número de cartas que possui.")
                guess = int(input("Dê outro palpite: "))

    return guess

def make_move():
    global MY_CARDS, TABLE_CARD
    ordered_cards = ['AE', '2E', '3E', '4E', '5E', '6E', '7E', 'JE', 'QE', 'KE', 
                     'AC', '2C', '3C', '4C', '5C', '6C', '7C', 'JC', 'QC', 'KC', 
                     'AO', '2O', '3O', '4O', '5O', '6O', '7O', 'JO', 'QO', 'KO', 
                     'AP', '2P', '3P', '4P', '5P', '6P', '7P', 'JP', 'QP', 'KP']

    move = {}
    is_playing = False
    response = input("Gostaria de fazer a jogada? [S/N]\nSe optar por não jogar, você passará sua vez! ")
    while True:
        if response.lower() in ["s","sim"]:
            while len(move) == 0 and (response.lower() not in ["s", "sim"]):
                target = input("Informe a carta de sua jogada: ").upper()
        
                if target in MY_CARDS:
                    print(f'[DEBUG] {target} está presente nas cartas que possui.')
            
                    target_index = ordered_cards.index(target)
                    print(f"target: {target}")
                    print(f"target_index: {target_index}")
                    table_card_index = ordered_cards.index(TABLE_CARD)
                    print(f"TABLE_CARD: {TABLE_CARD}")
                    print(f"table_card_index: {table_card_index}")
            
                    if target_index > table_card_index:
                        MY_CARDS.pop(target_index)
                        TABLE_CARD = target
                        move = target
                        print(f'Você jogou {target}.')
                        break
                    else:
                        print(f'A carta selecionada é mais fraca que {TABLE_CARD}! Tente novamente.')
                else:
                    print(f'{target} não está presente nas cartas que possui: {MY_CARDS}. Tente novamente.')
        
                #if len(move) == 0:
                #    response = input("Gostaria de tentar novamente? [S/N] ")
    
        elif response.lower() in ["n", "não", "nao"]:
            print("Você passou a sua vez.")
            move = -1
            break
        else:
            response = input("Ops! Sua resposta não foi interpretada como uma carta do baralho, tente novamente: ")
    
    return move


# Função para processar as mensagens do dealer
def dealer(sock, message):
    global TOKEN, MY_LIST, GUESSES, GLOBAL, MOVES, COUNT_MOVES
    print(f"MINHA LISTA AGR: {MY_LIST}")
    print(f"[DEBUG] Recebi uma mensagem! {message}")
    if message["type"] != "token" and message["from_player"] != MY_ID and message["to_player"] == MY_ID:
        if message["type"] == "receive_guesses":
            # Armazena o palpite
            if message["from_player"] != (MY_ID+3)%4:
                GUESSES[message['from_player']] = message["data"]
                print(f"Palpites atualemente: {GUESSES} !!!!!")
                print(f"Passando a mensagem: {message}")
                pass_message(sock, message)
            else:
                GUESSES[message["from_player"]] = message["data"]
                guess = take_guess(1)
                GUESSES[MY_ID] = guess
                print(f"[DEBUG] Palpites completos: {GUESSES}")
                # Preparo das mensagens com a info dos palpites
                # de forma a deixar o carteador por último
                for i in range(1,4):
                    msg = {
                        "type":"inform_guesses",
                        "from_player": MY_ID,
                        "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                        "data": GUESSES
                    }
                    MY_LIST.append(msg)
                    print(f"[DEBUG] Fez o appende de: {msg}")
                msg = {
                    "type":"inform_guesses",
                    "from_player": MY_ID,
                    "to_player": MY_ID,
                    "data": GUESSES
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o appende de: {msg}")
                #print(f"Vou começar a mandar os palpites: {MY_LIST}")
                #msg = MY_LIST.pop(0)
                #print(f"Estou enviando a mensgaem: {msg}")
                pass_message(sock, message)
        elif message["type"] == "inform_move":
            if message["from_player"] != (MY_ID+3)%4:
                COUNT_MOVES[message["from_player"]] += 1
                MOVES[message["from_player"]] = message["data"]
                print(f"Passando a mensagem: {message}")
                pass_message(sock, message)
            else:
                COUNT_MOVES[message["from_player"]] += 1
                MOVES[message["from_player"]] = message["data"]
                move = make_move()
                COUNT_MOVES[MY_ID] += 1
                MOVES[MY_ID] = move
                print(f"Todo mundo ja fez a jogada: {MOVES}; contador: {COUNT_MOVES}")
                print("Agr precisamos entender se basta dar uma volta de jogadas ou se vai continuando a dar voltas.... To be implementado....")
                a = input("Chegoooou até aquiii")
                #print(f"Passando a mensagem: {message}")
                #pass_message(sock, message)
        else:
            print(f"Passando a mensagem: {message}")
            pass_message(sock, message)
    elif message["from_player"] == MY_ID and message["to_player"] == MY_ID:
        #if message["type"] == "take_guesses":
        #    guess = take_guess(1)
        #    GUESSES[MY_ID] = guess
        #    print(f"Palpites completos: {GUESSES}")
        #    TOKEN = False
        #    msg = {
        #        "type": "token",
        #        "from_player": MY_ID,
        #        "to_player": NEXT_ID,
        #        "data": []
        #   }
        #    print(f"[DEBUG] Paasando bastão: {msg}")
        #    send_message(sock, msg, NEXT_IP, NEXT_PORT)
        #if message["type"] == "receive_guesses":
        #    guess = take_guess(1)
        #    GUESSES[MY_ID] = guess
        #    print(f"palpites completos: {GUESSES}")
        #    # Preparo das mensagens com a info dos palpites 
        #    # de forma a deixar o carteador por último
        #    for i in range(1, 4):
        #        msg = {
        #            "type": "inform_guesses",
        #            "from_player": MY_ID,
        #            "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
        #            "data": GUESSES
        #        }
        #        MY_LIST.append(msg)
        #        print(f"[DEBUG] Fez o append de: {msg}")
        #    msg = {
        #        "type": "inform_guesses",
        #        "from_player": MY_ID,
        #        "to_player": MY_ID,
        #        "data": GUESSES
        #    }
        #    MY_LIST.append(msg)
        #    print(f"[DEBUG] Fez o append de: {msg}")
        #    print(f"Passando a mensagem: {message}")
        #    pass_message(sock, message)
        if message['type'] == "inform_guesses":
            print("Palpites: ")
            for i in range(len(message['data'])):
                print(f"Jogador {i + 1}: {message['data'][i]}")
            # Prepara as mensagens solicitando que façam um movimento
            for i in range(1, 4):
                msg = {
                    "type": "make_move",
                    "from_player": MY_ID,
                    "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
                    "data": []
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o append de: {msg}")
            #msg = {
            #    "type": "make_move",
            #    "from_player": MY_ID,
            #    "to_player": MY_ID,
            #    "data": []
            #}
            #MY_LIST.append(msg)
            #print(f"[DEBUG] Fez o append de: {msg}")
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Passando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        elif message["type"] == "make_move": # ISSO AQUI NAO DEVE ESTAR MAIS SENDO USADO !!!
            move = input("Informe sua jogada: ")
            MOVES[MY_ID] = move
            print(f"[DEBUG] MOVIMENTOS: {MOVES}")
            a = input("Chegou até aqui!")
        else:
            print(f"Passando a mensagem: {message}")
            pass_message(sock, message)
    elif TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        print(f"[DEBUG] Recebi/estou com o token!")

        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"[DEBUG] Enviando mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Passando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    else:
        pass_message(sock, message)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    global TOKEN, MY_LIST, MY_CARDS, TABLE_CARD
    if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"[DEBUG] Estou enviando a mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Estou passando o bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    elif message["to_player"] == MY_ID:
        print(f"Recebi uma mensagem: {message}")
        if message["type"] == "init" and message["to_player"] == MY_ID:
            global DEALER_ID, TABLE_CARD
            DEALER_ID = message["from_player"]
            MY_CARDS = message['data']
            TABLE_CARD = MY_CARDS.pop()
            print(f"Manilha: {TABLE_CARD}")
            print(f"Jogador {MY_ID} recebeu suas cartas: {MY_CARDS}.")
            pass_message(sock, message)
        elif message["type"] == "take_guesses":
            guess = take_guess()
            msg = {
                "type": "receive_guesses",
                "from_player": MY_ID,
                "to_player": DEALER_ID,
                "data": guess
            }
            MY_LIST.append(msg)
            print(f"[DEBUG] Fez o append de: {msg}")
            pass_message(sock, message)
        elif message["type"] == "inform_guesses":
            print(f"Palpites:")
            for i in range(len(message["data"])):
                print(f"Jogador {i + 1}: {message['data'][i]}.")
            pass_message(sock, message)
        elif message["type"] == "make_move":
            # definir a função make_move, que atualiza TABLE_CARD e  precisa verificar se o jogador que fazer a jogada e se é possivel fazê-la [-1: se nao quiser/puder fazer; move: se puder e quiser fazer] 
            move = make_move()
            # msg = {
            #     "type": "inform_move",
            #     "from_player": MY_ID,
            #     "to_player": DEALER_ID,
            #     "data": move
            # }
            # MY_LIST.append(msg)
            # print(f"[DEBUG] Fez o append de: {msg}")
            for i in range(1,4):
                msg = {
                    "type":"inform_move",
                    "from_player": MY_ID,
                    "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                    "data": move
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o appende de: {msg}")
            pass_message(sock, message)
        elif message["type"] == "inform_move":
            if message["data"] != -1:
                print(f"O jogador {message['from_player']}+1 fez a seguinte jogada: {message['data']}.")
                TABLE_CARD = message["data"]
            else:
                print(f"O jogador {message['from_player']}+1 passou a vez.")
            pass_message(sock, message)
    else:
        pass_message(sock, message)

# Função para processar mensagens recebidas
def process_message(sock, message):
    if IS_DEALER:
        dealer(sock, message)
    else:
        normal_player(sock, message)

# Função para criar socket UDP
def create_socket(num_player):
    global MY_ID, MY_IP, MY_PORT, NEXT_ID, NEXT_IP, NEXT_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MY_ID = num_player - 1
    MY_IP = PLAYERS_IPS[MY_ID]
    MY_PORT = PLAYERS_PORTS[MY_ID]
    NEXT_ID = (MY_ID + 1) % 4
    NEXT_IP = PLAYERS_IPS[NEXT_ID]
    NEXT_PORT = PLAYERS_PORTS[NEXT_ID]
    sock.bind((MY_IP, MY_PORT))
    print(f"[DEBUG] MY_ID: {MY_ID}, MY_IP: {MY_IP}, MY_PORT: {MY_PORT}")
    print(f"[DEBUG] NEXT_ID: {NEXT_ID}, NEXT_IP: {NEXT_IP}, NEXT_PORT: {NEXT_PORT}")
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message, ip, port):
    sock.sendto(json.dumps(message).encode(), (ip, port))

# Função para passar a mensagem adiante
def pass_message(sock, message):
    send_message(sock, message, NEXT_IP, NEXT_PORT)

# Função para receber e processar mensagens
def receive_message(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)

def main():
    cards = []
    if len(sys.argv) > 1:
        sock = create_socket(int(sys.argv[1]))
        if len(sys.argv) > 2 and sys.argv[2] == 'start':
            init_game(sock)
        receive_message(sock)
    else:
        print("O código espera receber como parâmetro: python3 universal.py <num_jogador> <start>")
        print("Sendo o segundo parâmetro opcional, pois indica quem será o primeiro carteador.")
        sys.exit(1)

if __name__ == "__main__":
    main()
