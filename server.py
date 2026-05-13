import socket
import threading
import time
import select

# =========================
# Server Configuration
# =========================

HOST = '1.1.1.1'
PORT = 5555

# Create TCP socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# =========================
# Matchmaking Queue System
# =========================

# List of players waiting for a match
player_queue = []

# Lock to prevent race conditions when multiple threads access the queue
queue_lock = threading.Lock()


# =========================
# Game Session Handler
# =========================

def handle_game(p1_conn, p2_conn):
    """
    Handles a single PvP game session between two connected players.
    This function creates a bidirectional relay system between both clients.
    """

    def forward_data(sender, receiver, player_num):
        """
        Continuously forwards data from one player to the other.

        This acts as a real-time relay tunnel:
        Player A → Server → Player B (and vice versa)
        """
        try:
            while True:
                data = sender.recv(4096)

                # If no data is received, the connection is closed
                if not data:
                    break

                # Forward received data to the opponent
                receiver.sendall(data)

        except:
            # Any network error will break the forwarding loop
            pass

        finally:
            print(f"[DISCONNECT] Player {player_num} left the game.")
            sender.close()

    # Create two threads for bidirectional communication
    t1 = threading.Thread(target=forward_data, args=(p1_conn, p2_conn, 1))
    t2 = threading.Thread(target=forward_data, args=(p2_conn, p1_conn, 2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("[MATCH ENDED] The game session is over.")


# =========================
# Queue Cleaner System
# =========================

def clean_queue():
    """
    Background process that continuously cleans invalid players from the queue.

    It removes:
    - Disconnected sockets
    - Players who pressed ESC / CANCEL
    """

    while True:
        with queue_lock:
            if len(player_queue) > 0:
                try:
                    # Check which sockets are readable (active or closed)
                    readable, _, _ = select.select(player_queue, [], [], 0)

                    for conn in readable:
                        try:
                            data = conn.recv(1024)

                            # If no data or CANCEL message → remove player
                            if not data or b"CANCEL" in data:
                                if conn in player_queue:
                                    player_queue.remove(conn)
                                    print(f"[QUEUE] Player canceled. Waiting: {len(player_queue)}")
                                    conn.close()

                        except:
                            # If connection is broken
                            if conn in player_queue:
                                player_queue.remove(conn)
                                print(f"[QUEUE] Player disconnected. Waiting: {len(player_queue)}")
                                conn.close()

                except Exception:
                    pass

        time.sleep(0.5)


# =========================
# Matchmaking System
# =========================

def matchmaking():
    """
    Continuously matches players from the queue in pairs.

    Flow:
    1. Check if at least 2 players are waiting
    2. Remove them from queue (FIFO order)
    3. Notify both players
    4. Start a new game session thread
    """

    while True:
        with queue_lock:
            if len(player_queue) >= 2:

                # Take first two players in queue
                p1_conn = player_queue.pop(0)
                p2_conn = player_queue.pop(0)

                p1_alive = True
                p2_alive = True

                # Notify players they were matched
                try:
                    p1_conn.sendall(b"MATCH_FOUND|1")
                except:
                    p1_alive = False

                try:
                    p2_conn.sendall(b"MATCH_FOUND|2")
                except:
                    p2_alive = False

                # Start game if both players are still connected
                if p1_alive and p2_alive:
                    print("[MATCHED] Starting new game session...")
                    threading.Thread(
                        target=handle_game,
                        args=(p1_conn, p2_conn)
                    ).start()

                else:
                    print("[ERROR] Match failed due to disconnect.")

                    # Return alive player back to queue
                    if p1_alive:
                        player_queue.insert(0, p1_conn)
                    elif p2_alive:
                        player_queue.insert(0, p2_conn)

        time.sleep(1)


# =========================
# Connection Handler
# =========================

def accept_connections():
    """
    Main server loop.

    Responsibilities:
    - Accept new TCP connections
    - Add players to matchmaking queue
    - Start background systems (matchmaking + cleanup)
    """

    print(f"[STARTING] Server running on {HOST}:{PORT}")

    # Start background threads
    threading.Thread(target=matchmaking, daemon=True).start()
    threading.Thread(target=clean_queue, daemon=True).start()

    # Main accept loop
    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected")

        with queue_lock:
            player_queue.append(conn)
            print(f"[QUEUE] Players waiting: {len(player_queue)}")


# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    accept_connections()