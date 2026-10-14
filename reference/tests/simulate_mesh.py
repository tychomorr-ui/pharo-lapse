import json, os, shutil
BASE = os.path.expanduser("~/mesh-sim")
REACH = {"node-a":["node-b"], "node-b":["node-a","node-c"], "node-c":["node-b"]}

def read_and_clear(node):
    d = f"{BASE}/{node}/inbox"
    os.makedirs(d, exist_ok=True)
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(f"{d}/{fn}") as f:
                out.append(json.load(f))
            os.remove(f"{d}/{fn}")
    return out

def deliver(node, env):
    d = f"{BASE}/{node}/inbox"
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/{env['msg_id']}.json", "w") as f:
        json.dump(env, f)

def main():
    shutil.rmtree(BASE, ignore_errors=True)
    env = {"msg_id":"0001","sender_peer_id":"node-a","recipient_peer_id":"node-c",
           "body":"HELLO-FROM-A","route_history":[]}
    print(f"[A] built {env['msg_id']}")
    env["route_history"].append("node-a")
    deliver("node-b", env)
    print("[A] sent to B")

    for env in read_and_clear("node-b"):
        print(f"[B] got {env['msg_id']} route={env['route_history']}")
        if env["recipient_peer_id"] == "node-b":
            print("[B] delivered")
            return
        visited = set(env["route_history"])
        env["route_history"].append("node-b")
        for peer in REACH["node-b"]:
            if peer not in visited:
                deliver(peer, env)
                print(f"[B] -> {peer}")
                break

    for env in read_and_clear("node-c"):
        print(f"[C] got {env['msg_id']} route={env['route_history']}")
        print(f"[C] DELIVERED: {env['body']}")

main()
