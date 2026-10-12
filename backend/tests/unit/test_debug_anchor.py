from app.services.earring_detector import DebugStateEarringDetector


def test_debug_anchor_is_normalized_attachment_not_a_box_center():
    anchor = DebugStateEarringDetector().detect_from_state(
        {
            "jewelry_id": "E123",
            "jewelry_type": "earring",
            "left": {"x": 0.423, "y": 0.371, "visible": True, "rotation": 3.2, "scale": 1.02},
        },
        "left",
    )
    assert anchor is not None
    assert anchor.source == "debug"
    assert anchor.x == 0.423
    assert anchor.y == 0.371
    assert anchor.confidence == 0.99
    assert anchor.jewelry_id == "E123"


def test_debug_anchor_rejects_pixel_coordinates():
    anchor = DebugStateEarringDetector().detect_from_state(
        {"left_earring": {"anchor_x": 420, "anchor_y": 180, "visible": True}},
        "left",
    )
    assert anchor is not None
    assert anchor.visible is False
    assert anchor.x is None
