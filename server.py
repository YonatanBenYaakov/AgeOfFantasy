import socket
import threading
import time
import select

# הגדרות השרת
HOST = '10.0.0.11'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# --- משתני ניהול תור ---
player_queue = []
queue_lock = threading.Lock()


def handle_game(p1_conn, p2_conn):
    def forward_data(sender, receiver, player_num):
        try:
            while True:
                # <-- התיקון כאן! שינינו מ-1024 ל-4096
                data = sender.recv(4096)
                if not data:
                    break
                receiver.sendall(data)
        except:
            pass
        finally:
            print(f"[DISCONNECT] Player {player_num} left the game.")
            sender.close()

    t1 = threading.Thread(target=forward_data, args=(p1_conn, p2_conn, 1))
    t2 = threading.Thread(target=forward_data, args=(p2_conn, p1_conn, 2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("[MATCH ENDED] The game session is over.")


def clean_queue():
    """
    פונקציה שרצה ברקע וכל חצי שנייה מנקה מהתור אנשים שלחצו אסקייפ או סגרו את החלון.
    """
    while True:
        with queue_lock:
            if len(player_queue) > 0:
                try:
                    # select בודק האם אחד מהשחקנים בתור שלח מידע או סגר את הצינור
                    readable, _, _ = select.select(player_queue, [], [], 0)
                    for conn in readable:
                        try:
                            data = conn.recv(1024)
                            # אם הוא סגר את החיבור או ששלח במפורש את הפקודה שיצרנו
                            if not data or b"CANCEL" in data:
                                if conn in player_queue:
                                    player_queue.remove(conn)
                                    print(f"[QUEUE] Player canceled (ESC). Current players waiting: {len(player_queue)}")
                                    conn.close()
                        except:
                            # אם יש שגיאה (החיבור נפל לגמרי)
                            if conn in player_queue:
                                player_queue.remove(conn)
                                print(f"[QUEUE] Player disconnected. Current players waiting: {len(player_queue)}")
                                conn.close()
                except Exception as e:
                    pass
        time.sleep(0.5)


def matchmaking():
    """
    פונקציה שרצה בלולאה ברקע כל הזמן ומשדכת שחקנים מהתור.
    """
    while True:
        with queue_lock:
            # התנאי: יש לפחות 2 שחקנים בתור
            if len(player_queue) >= 2:
                p1_conn = player_queue.pop(0)
                p2_conn = player_queue.pop(0)

                p1_alive = True
                p2_alive = True

                try:
                    p1_conn.sendall(b"MATCH_FOUND|1")
                except Exception:
                    p1_alive = False

                try:
                    p2_conn.sendall(b"MATCH_FOUND|2")
                except Exception:
                    p2_alive = False

                if p1_alive and p2_alive:
                    print("[MATCHED] 2 players pulled from queue. Starting match in a new thread...")
                    threading.Thread(target=handle_game, args=(p1_conn, p2_conn)).start()
                else:
                    print("[ERROR] Someone disconnected while trying to start the match.")
                    if p1_alive:
                        player_queue.insert(0, p1_conn)
                    elif p2_alive:
                        player_queue.insert(0, p2_conn)

        time.sleep(1)


def accept_connections():
    print(f"[STARTING] Server is running and listening on {HOST}:{PORT}")

    # מפעילים את השידוכים ואת מנקה התור ברקע
    threading.Thread(target=matchmaking, daemon=True).start()
    threading.Thread(target=clean_queue, daemon=True).start()

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected. Adding to queue...")

        with queue_lock:
            player_queue.append(conn)
            print(f"[QUEUE] Current players waiting: {len(player_queue)}")


if __name__ == "__main__":
    accept_connections()