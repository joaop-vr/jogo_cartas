import socket
import json
import sys
import random

# Configurações da rede
#TABLE_CARD = 0
SHACKLE = 0
ROUND = 0
TOKEN = False
IS_DEALER = False
DEALER_ID = 0
HP = 7
SHUFFLED_CARDS = []
CARDS = []
MY_LIST = []
MY_CARDS = []
COUNT_WINS = [0, 0, 0, 0]
GUESSES = [None, None, None, None]
MOVES = [None, None, None, None]
PLAYERS_HP = [7, 7, 7, 7]
PLAYERS_IPS = ["10.254.223.39", "10.254.223.40", "10.254.223.41", "10.254.223.38"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
MY_ID = 0
MY_IP = 0
MY_PORT = 0
NEXT_ID = 0
NEXT_IP = 0
NEXT_PORT = 0

# Função de inicialização do jogo
def init_round(sock):
    global TOKEN, MY_LIST, IS_DEALER, ROUND, TABLE_CARD, MY_CARDS

    # O carteador é o primeiro a receber um token
    TOKEN = True

    # Contador de rodadas
    ROUND = ROUND + 1

    # Distribui as cartas para os jogadores e armazena em 'player_cards'
    player_cards = distribute_cards()

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Prepara as mensagens de distribuição de cartas
    for i in range(1, 4):
        msg = {
            "type": "init",
            "from_player": MY_ID,
            "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
            "data": player_cards.pop(0)
        }
        MY_LIST.append(msg)

    # Guardando as cartas do carteador
    MY_CARDS = player_cards.pop(0)[0]
    print_init_infos()

    # Prepara as mensagens de solicitação de palpites
    for i in range(1,4):
        msg = {
            "type": "take_guesses",
            "from_player": MY_ID,
            "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
            "data": []
        }
        MY_LIST.append(msg)
    # Envia a primeira mensagem da lista
    msg = MY_LIST.pop(0)
    send_message(sock, msg, NEXT_IP, NEXT_PORT)

# Função para distribuir cartas
def distribute_cards():
    global ROUND, SHUFFLED_CARDS
    
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    
    for i in range(ROUND):  # ROUND == número de cartas sorteadas
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())

    # Embaralhando o baralho
    SHUFFLED_CARDS = values[:]
    random.shuffle(SHUFFLED_CARDS)

    # Sorteando a manilha (SHACKLE)
    global SHACKLE
    SHACKLE = SHUFFLED_CARDS.pop()
    powerful_card = 0 
    try:
        # Encontra a posição da Manilha
        index = values.index(SHACKLE)
        # Calcula a posição do próximo elemento, considerando a circularidade
        next_index = (index + 1) % len(values)
        # Remove o próximo elemento
        powerful_card = values.pop(next_index)
    except ValueError:
        print(f"Elemento {SHACKLE} não encontrado na lista.")
    
    global CARDS
    CARDS = values[:]
    CARDS.append(powerful_card)  # Coloca a carta que está à direita da Manilha no extremo direito do "values" de cartas
    
    output = [[] for _ in range(4)]
    for i in range(4):
        output[i].append(players_cards[i])
        output[i].append(SHACKLE)
        output[i].append(CARDS)

    # output[i] = [[cartas sorteadas do player],[Manilha],[configuração do poder das cartas nessa partida]]
    return output

def print_init_infos():
    print(f"Rodada: {ROUND}")
    print(f"Manilha: {SHACKLE}")
    print(f"Configuração da partida: {CARDS}")
    print(f"Suas cartas: {MY_CARDS}.")
    return 
    
def print_guesses(guesses):
    print(f"Palpites:")
    for i in range(len(guesses)):
        print(f"Jogador {i + 1}: {guesses[i]}.")
    return 

def print_previous_moves(moves):
    print(f"Cartas já jogadas: {moves}")
    return

def print_moves(moves):
    for i in range(len(moves)):
        print(f"O jogador {i}+1 fez a seguinte jogada: {moves[i]}.")
    return
    
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
    global MY_CARDS
    move = {}
    print(f"Suas cartas: {MY_CARDS}")
    response = input("Informe sua jogada: ").upper()
    while response not in MY_CARDS:
        response = input("Ops! Sua resposta não foi interpretada como uma carta que você possue, tente novamente: ")
    MY_CARDS.remove(response)
    return response

def count_points():
    a = input("To na função count_poinst(), precisa implementar a dinamica de jogar carta igual manilha pra ent analisar os naipes!.... (aperta ctrl+C ai vai)")
    index_players = []
    index_players.append(CARDS.index(MOVES[0][0]))
    index_players.append(CARDS.index(MOVES[1][0]))
    index_players.append(CARDS.index(MOVES[2][0]))
    index_players.append(CARDS.index(MOVES[3][0]))
    if MOVES[0] == MOVES[1]:
        index_player[0] = -1
        index_player[1] = -1
        print("Enbuxou as cartas dos jogadores 1 e 2!")
        if MOVES[2] == MOVES[3]:
            index_player[2] = -1
            index_player[3] = -1
            print("Enbuxou as cartas dos jogadores 3 e 4!")
    elif MOVES[1] == MOVES[2]:
        index_player[1] = -1
        index_player[2] = -1
        print("Enbuxou as cartas dos jogadores 2 e 3!")
        if MOVES[0] == MOVES[3]:
            index_player[0] = -1
            index_player[3] = -1
            print("Enbuxou as cartas dos jogadores 1 e 4!")
    elif MOVES[2] == MOVES[3]:
        index_player[2] = -1
        index_player[3] = -1
        print("Enbuxou as cartas dos jogadores 3 e 4!")

    sum = 0
    for i in index_players:
        sum += i

    if sum == -4:
        print(f"Houve 2 enbuxadas consecutivas! Portanto, ninguém ganhou essa rodada.")
    else:
        max_value = max(index_players)
        index_winner = index_players.index(max_value)
        global COUNT_WINS
        COUNT_WINS[index_winner] += 1
        print(f"Quem ganhou a rodada {ROUND} foi o jogador {index_winner}")
    return 

def reset_vars():
    global SHACKLE, DEALER_ID, CARDS, COUNT_WINS, GUESSES, MOVES
    SHACKLE = 0
    DEALER_ID = 0
    CARDS = []
    COUNT_WINS = [0, 0, 0, 0]
    GUESSES = [None, None, None, None]
    MOVES = [None, None, None, None]
    return 
    
def finish_round():
    #count_points()  # Supondo que esta função atualize as variáveis GUESSES e COUNT_WINS

    # Subtrai elemento por elemento
    final_points = [guess - win for guess, win in zip(GUESSES, COUNT_WINS)]
    
    # Atualiza os pontos negativos diretamente na lista
    final_points = [-point if point > 0 else point for point in final_points]

    print("Estou dentro da função finish_round()")
    print(f"GUESSES: {GUESSES}")
    print(f"COUNT_WINS: {COUNT_WINS}")
    print(f"final_points: {final_points}")
    
    return final_points

# Função para processar as mensagens do dealer
def dealer(sock, message):
    global TOKEN, MY_LIST, GUESSES, GLOBAL, MOVES, COUNT_MOVES
    #print(f"MINHA LISTA AGR: {MY_LIST}")
    print(f"[DEBUG] Recebi uma mensagem! {message}")
    #a = input(f"\nCheckpoint")
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
                pass_message(sock, message)
        elif message["type"] == "informing_move":
            if message["from_player"] != (MY_ID+3)%4:
                MOVES[message["from_player"]] = message["data"]
            else:
                # Completou um ciclo!
                MOVES[message["from_player"]] = message["data"]
                #print(f"O jogador {message['from_player']}+1 fez a seguinte jogada: {message['data']}.")
                move = make_move()
                MOVES[MY_ID] = move
                print(f"[DEBUG] MOVES da rodada: {MOVES}")
                count_points()
                # Prepara as mensagem informando o move do carteador
                for i in range(1,4):
                    msg = {
                        "type":"informing_move",
                        "from_player": MY_ID,
                        "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                        "data": MOVES
                    }
                    MY_LIST.append(msg)
                    print(f"[DEBUG] Fez o appende de: {msg}")
                msg = {
                    "type":"informing_move",
                    "from_player": MY_ID,
                    "to_player": MY_ID, 
                    "data": MOVES
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o appende de: {msg}")
            print(f"Passando a mensagem: {message}")
            pass_message(sock, message)
        else:
            print(f"Passando a mensagem: {message}")
            pass_message(sock, message)
    elif message["from_player"] == MY_ID and message["to_player"] == MY_ID:
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
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Passando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        elif message["type"] == "informing_move":
            for i in range(len(message["data"])):
                print(f"O jogador {i}+1 fez a seguinte jogada: {message['data'][i]}.")
            if len(MY_CARDS) >= 1:   # Completou um ciclo mas ainda há mais cartas na mão 
                # Prepara as mensagem informando o move do carteador
                for i in range(1,4):
                    msg = {
                        "type":"make_move",
                        "from_player": MY_ID,
                        "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                        "data": []
                    }
                    MY_LIST.append(msg)
                print(f"[DEBUG] Fez o appende de: {msg}")
                #pass_message(sock, message)
            elif len(MY_CARDS) == 0: # Completou uma volta e não tem mais uma carta na mao do carteador
                print(f"A rodada acabou, já vou contabilizar os ponto e deixar as mensagens deles engatilhadas!")
                end_round_info = finish_round()
                for i in range(1, 4):
                    msg = {
                        "type": "end_round_info",
                        "from_player": MY_ID,
                        "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
                        "data": end_round_info
                    }
                    MY_LIST.append(msg)
                    print(f"[DEBUG] Fez o append de: {msg}")
                msg = {
                    "type": "end_round_info",
                    "from_player": MY_ID,
                    "to_player": MY_ID,  # Isso possibilita a universalização do carteador
                    "data": end_round_info
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o append de: {msg}")
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Passando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        elif message["type"] == "end_round_info":
            global HP
            print(f"Informações da rodada {ROUND}: {message['data']}")
            print(f"HP no inicio da rodada: {HP}")
            HP = HP + message["data"][MY_ID]
            print(f"HP ao final da rodada: {HP}")
            print("Estamos no elif message['type'] == 'end_round_info', vamo ve se funcionou.")
            a = input()
            reset_vars()
            for i in range(1, 4):
                msg = {
                    "type": "reset_vars",
                    "from_player": MY_ID,
                    "to_player": (MY_ID + i) % 4,  # Isso possibilita a universalização do carteador
                    "data": []
                }
                MY_LIST.append(msg)
                print(f"[DEBUG] Fez o append de: {msg}")
            global IS_DEALER
            IS_DEALER = False
            msg = {
                "type": "token_dealer",
                "from_player": MY_ID,
                "to_player": NEXT_ID,  # Isso possibilita a universalização do carteador
                "data": []
            }
            MY_LIST.append(msg)
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
# def normal_player(sock, message):
#     global TOKEN, MY_LIST, MY_CARDS
#     #print(f"Recebi uma mensagem: {message}")
#     #a = input("Checkpoint")
#     if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
#         TOKEN = True
#         if len(MY_LIST) > 0:
#             msg = MY_LIST.pop(0)
#             print(f"[DEBUG] Estou enviando a mensagem: {msg}")
#             send_message(sock, msg, NEXT_IP, NEXT_PORT)
#         else:
#             TOKEN = False
#             msg = {
#                 "type": "token",
#                 "from_player": MY_ID,
#                 "to_player": NEXT_ID,
#                 "data": []
#             }
#             print(f"[DEBUG] Estou passando o bastão: {msg}")
#             send_message(sock, msg, NEXT_IP, NEXT_PORT)
#     elif message["to_player"] == MY_ID:
#         print(f"Recebi uma mensagem: {message}")
#         #a = input(f"\nCheckpoint")
#         if message["type"] == "init":
#             global DEALER_ID, SHACKLE, CARDS, ROUND
#             DEALER_ID = message["from_player"]
#             aux = message['data']
#             MY_CARDS = aux[0]
#             SHACKLE = aux[1]
#             CARDS = aux[2]
#             ROUND = len(MY_CARDS)
#             print(f"Rodada: {ROUND}")
#             print(f"Manilha: {SHACKLE}")
#             print(f"Configuração da partida: {CARDS}")
#             print(f"Jogador {MY_ID} recebeu suas cartas: {MY_CARDS}.")
#             pass_message(sock, message)
#         elif message["type"] == "take_guesses":
#             guess = take_guess()
#             msg = {
#                 "type": "receive_guesses",
#                 "from_player": MY_ID,
#                 "to_player": DEALER_ID,
#                 "data": guess
#             }
#             MY_LIST.append(msg)
#             print(f"[DEBUG] Fez o append de: {msg}")
#             pass_message(sock, message)
#         elif message["type"] == "inform_guesses":
#             print(f"Palpites:")
#             for i in range(len(message["data"])):
#                 print(f"Jogador {i + 1}: {message['data'][i]}.")
#             pass_message(sock, message)
#         elif message["type"] == "make_move":
#             # definir a função make_move, que atualiza TABLE_CARD e  precisa verificar se o jogador que fazer a jogada e se é possivel fazê-la [-1: se nao quiser/puder fazer; move: se puder e quiser fazer] 
#             move = make_move()
#             msg = {
#                 "type":"informing_move",
#                 "from_player": MY_ID,
#                 "to_player": DEALER_ID, # Isso possibilita a universalização do carteador
#                 "data": move
#             }
#             MY_LIST.append(msg)
#             print(f"[DEBUG] Fez o appende de: {msg}")
#             pass_message(sock, message)
#         elif message["type"] == "informing_move":
#             for i in range(len(message["data"])):
#                 print(f"O jogador {i}+1 fez a seguinte jogada: {message['data'][i]}.")
#             pass_message(sock, message)
#         elif message["type"] == "end_round_info":
#             global HP
#             print(f"Informações finais da rodada {ROUND}: {message['data']}")
#             print(f"HP no inicio da rodada: {HP}")
#             HP = HP + message["data"][MY_ID]
#             print(f"HP ao final da rodada: {HP}")
#             a = input()
#             pass_message(sock, message)
#         elif message["type"] == "reset_vars":
#             reset_vars()
#             pass_message(sock, message)
#         elif message["type"] == "token_dealer":
#             global IS_DEALER 
#             IS_DEALER = True
#             init_round(sock)
#             receive_message(sock)
#     else:
#         pass_message(sock, message)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    global HP
    # Recebeu uma mensagem destinada a ele
    if HP > 0 and (message["broadcast"] == True or message["to_player"] == MY_ID):
        #print(f"Recebi uma mensagem: {message}")
        #a = input(f"\nCheckpoint")
        if message["type"] == "init":
            global DEALER_ID, SHACKLE, CARDS, ROUND
            DEALER_ID = message["from_player"]
            aux = message['data']
            MY_CARDS = aux[0]
            SHACKLE = aux[1]
            CARDS = aux[2]
            ROUND = len(MY_CARDS)
            print_init_infos()
            pass_message(sock, message)
        elif message["type"] == "take_guesses":
            message["ACKs"][MY_ID] = 1
            guess = take_guess()
            message["data"][MY_ID] = guess
            pass_message(sock, message)
        elif message["type"] == "informing_guesses":
            message["ACKs"][MY_ID] = 1
            print_guesses(message["data"])
            pass_message(sock, message)
        elif message["type"] == "make_move":
            message["ACKs"][MY_ID] = 1
            print_previous_moves(message["data"])
            move = make_move()
            message["data"][MY_ID] = move
            pass_message(sock, message)
        elif message["type"] == "informing_moves":
            message["ACKs"][MY_ID] = 1
            print_moves(message["data"])
            pass_message(sock, message)
        elif message["type"] == "round_info":
            # Imprime o ganahdor da sub-rodada
            print(f"Informações finais da rodada {ROUND}: {message['data']}")
            winner_index = message["data"][0]
            if winner_index != -1:
                print(f"Ganhador: Jogador {winner_index+1}")
            else:
                print("Não houve ganhador nessa sub-rodada!")

            # Atualiza as suas vidas
            print(f"HP no inicio da rodada: {HP}")
            HP = HP + message["data"][1][MY_ID]
            print(f"HP ao final da rodada: {HP}")
            pass_message(sock, message)
        elif message["type"] == "reset_vars":
            reset_vars()
            pass_message(sock, message)
        elif message["type"] == "token_dealer":
            global IS_DEALER 
            IS_DEALER = True
            init_round(sock)
            receive_message(sock)
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
def send_message(sock, message):
    sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))

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
    if len(sys.argv) > 1:
        sock = create_socket(int(sys.argv[1]))
        if len(sys.argv) > 2 and sys.argv[2] == 'start':
            init_round(sock)
        receive_message(sock)
    else:
        print("O código espera receber como parâmetro: python3 universal.py <num_jogador> <start>")
        print("Sendo o segundo parâmetro opcional, pois indica quem será o primeiro carteador.")
        sys.exit(1)

if __name__ == "__main__":
    main()

