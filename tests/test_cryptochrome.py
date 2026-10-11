import unittest

from cryptochrome.consensus import outbox_depths
from cryptochrome.heading import synthesize_heading
from cryptochrome.mesh import parse_wg_dump
from cryptochrome.phase import Phase, compute_phase, phase_from_peers
from cryptochrome.signals import read_arrival_history, sensor_snapshot


class CryptochrometerTests(unittest.TestCase):
    def test_day_threshold(self):
        self.assertEqual(compute_phase(2, 4), Phase.DAY)

    def test_twilight_band(self):
        self.assertEqual(compute_phase(1, 4), Phase.TWILIGHT)

    def test_night_threshold(self):
        self.assertEqual(compute_phase(0, 4), Phase.NIGHT)

    def test_empty_pinned_set_is_night(self):
        self.assertEqual(compute_phase(0, 0), Phase.NIGHT)

    def test_invalid_phase_counts_rejected(self):
        with self.assertRaises(ValueError):
            compute_phase(3, 2)

    def test_wireguard_dump_is_parsed(self):
        dump = "\t".join(["pub", "none", "10.0.0.2:51820", "10.0.0.2/32", "42", "100", "200", "phone"])
        state = parse_wg_dump([dump])
        self.assertTrue(state["phone"].reachable)
        self.assertEqual(state["phone"].rx_bytes, 100)

    def test_phase_uses_only_pinned_peers(self):
        dump = "\t".join(["pub", "none", "10.0.0.2:51820", "10.0.0.2/32", "42", "1", "1", "phone"])
        state = parse_wg_dump([dump])
        self.assertEqual(phase_from_peers(state, {"phone", "relay", "relay-2", "relay-3"}), Phase.TWILIGHT)

    def test_arrival_history_is_ordered(self):
        history = read_arrival_history(rows=[("phone", "2026-01-02"), ("phone", "2026-01-03")])
        self.assertEqual(history["phone"], ["2026-01-02", "2026-01-03"])

    def test_signal_snapshot_has_last_arrival(self):
        snapshot = sensor_snapshot({"phone": ["a", "b"]})
        self.assertEqual(snapshot["phone"]["last_arrival"], "b")
        self.assertEqual(snapshot["phone"]["arrivals"], 2)

    def test_consensus_excludes_terminal_work(self):
        self.assertEqual(outbox_depths(rows=[("phone", 2), ("relay", 1)]), {"phone": 2, "relay": 1})

    def test_heading_excludes_visited_and_recipient(self):
        heading = synthesize_heading(
            reachable_peer_ids={"relay-a", "relay-b", "phone"},
            arrival_history={}, queue_depths={}, route_history=["penguin"],
            recipient_peer_id="phone",
        )
        self.assertEqual(heading.selected_peer, "relay-a")

    def test_heading_is_deterministic_and_weighted(self):
        heading = synthesize_heading(
            reachable_peer_ids={"relay-a", "relay-b"},
            arrival_history={"relay-b": ["1", "2"]},
            queue_depths={"relay-a": 1, "relay-b": 0},
        )
        self.assertEqual(heading.selected_peer, "relay-b")
        self.assertEqual(heading.candidates, ("relay-b", "relay-a"))


if __name__ == "__main__":
    unittest.main()
