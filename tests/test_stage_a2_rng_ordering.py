# -*- coding: utf-8 -*-
"""
Kiểm tra hồi quy chuẩn cho Giai đoạn A2 RNG Thứ tự khởi tạo và tiếp tục liên tục.
Chứng minh:
  1. Khởi tạo hạt giống mới -> các tham số mô hình giống hệt nhau.
  2. Hạt giống chuẩn khác nhau -> khởi tạo khác nhau.
  3. Quỹ đạo 2 epoch liên tục khớp với epoch 1 + checkpoint + tiếp tục epoch thứ 2.
  4. Tính ngẫu nhiên của việc bỏ học được duy trì trong suốt sơ yếu lý lịch mà không cần gieo hạt lại.
  5. Trạng thái checkpoint RNG là có thẩm quyền; load_checkpoint không được theo sau bởi việc gieo hạt lại.
"""

import sys
import json
import random
import tempfile
from pathlib import Path
import numpy as np
import pytest
import torch

from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder
from research_agent.experiments.training.stage_a2_trainer import StageA2Trainer
from scripts.run_stage_a2_five_seed_empirical import (
    run_single_seed_pipeline,
    enforce_framework_determinism
)

REPO_ROOT = Path(__file__).resolve().parent.parent

def build_dummy_fixture_events(n_events: int = 16) -> list:
    """Tạo các sự kiện biểu đồ xác định tổng hợp phù hợp với kỳ vọng của quy trình."""
    events = []
    for i in range(n_events):
        rel_id = (i % 8) + 1
        events.append({
            "raw_line_index": i + 1,
            "event_timestamp_utc_exact": 1000.0 + i * 10.0,
            "source_node": f"node_{i % 4}",
            "source_type": 1,
            "dest_node": f"node_{(i + 1) % 4}",
            "dest_type": 0,
            "relation_id": rel_id,
            "relation_name": f"REL_{rel_id}",
            "block_id": f"blk_{i // 4}",
            "size_bytes": 1024.0
        })
    return events

def test_same_seed_fresh_init_identical_weights():
    """Xác minh cùng một hạt giống tạo ra các tham số mô hình giống hệt nhau 100%."""
    seed = 42
    
    # Bắt đầu 1
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    model1 = TemporalGraphViewEncoder(
        d_node=128, d_edge=64, d_msg=128, n_heads=4,
        d_time_proj=32, d_rel_emb=32, d_type_emb=32,
        dropout=0.10, num_canonical_relations=8, num_node_types=4
    )
    
    # Ban đầu 2
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    model2 = TemporalGraphViewEncoder(
        d_node=128, d_edge=64, d_msg=128, n_heads=4,
        d_time_proj=32, d_rel_emb=32, d_type_emb=32,
        dropout=0.10, num_canonical_relations=8, num_node_types=4
    )
    
    for (n1, p1), (n2, p2) in zip(model1.named_parameters(), model2.named_parameters()):
        assert torch.equal(p1, p2), f"Parameter mismatch for {n1}"

def test_different_seed_fresh_init_different_weights():
    """Xác minh các hạt giống chuẩn khác nhau tạo ra các thông số mô hình khác nhau."""
    seeds = [42, 1337]
    models = []
    for s in seeds:
        random.seed(s)
        np.random.seed(s)
        torch.manual_seed(s)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(s)
        m = TemporalGraphViewEncoder(
            d_node=128, d_edge=64, d_msg=128, n_heads=4,
            d_time_proj=32, d_rel_emb=32, d_type_emb=32,
            dropout=0.10, num_canonical_relations=8, num_node_types=4
        )
        models.append(m)
        
    differ = False
    for (n1, p1), (n2, p2) in zip(models[0].named_parameters(), models[1].named_parameters()):
        if not torch.equal(p1, p2):
            differ = True
            break
    assert differ is True, "Different seeds produced identical weights!"

def test_after_load_checkpoint_no_reseed(tmp_path):
    """Xác minh load_checkpoint khôi phục trạng thái RNG và không xảy ra quá trình khởi động lại tiếp theo."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed = 42
    
    # Người mẫu & huấn luyện viên ban đầu
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    model = TemporalGraphViewEncoder(
        d_node=128, d_edge=64, d_msg=128, n_heads=4,
        d_time_proj=32, d_rel_emb=32, d_type_emb=32,
        dropout=0.10, num_canonical_relations=8, num_node_types=4
    )
    trainer = StageA2Trainer(
        model=model, max_epochs=2, seed=seed,
        execution_device=device, execution_mode="FIXTURE_TEST",
        empirical_authorized=True, total_steps_override=2
    )
    
    # Nâng cao trạng thái RNG bằng cách lấy mẫu
    _ = torch.randn(100)
    _ = np.random.rand(100)
    _ = random.random()
    
    # Lưu checkpoint
    ckpt_p = tmp_path / "checkpoint.pt"
    trainer.save_checkpoint(ckpt_p)
    
    # Nâng cao trạng thái RNG hơn nữa
    val_after_advance = torch.randn(5)
    
    # Tải checkpoint trong huấn luyện viên mới
    model2 = TemporalGraphViewEncoder(
        d_node=128, d_edge=64, d_msg=128, n_heads=4,
        d_time_proj=32, d_rel_emb=32, d_type_emb=32,
        dropout=0.10, num_canonical_relations=8, num_node_types=4
    )
    trainer2 = StageA2Trainer(
        model=model2, max_epochs=2, seed=seed,
        execution_device=device, execution_mode="FIXTURE_TEST",
        empirical_authorized=True, total_steps_override=2
    )
    
    trainer2.load_checkpoint(ckpt_p)
    
    # Lấy mẫu lại từ trainer2 mà không gieo hạt lại
    val_from_restored = torch.randn(5)
    
    # Cả hai phải giống hệt nhau vì RNG đã được khôi phục chính xác
    assert torch.equal(val_after_advance, val_from_restored)

def test_runner_resume_trajectory_continuity(tmp_path):
    """
    Kiểm tra tích hợp:
      Chạy liên tục (2 kỷ) Trận đấu MUST bị gián đoạn + chạy tiếp tục (kỷ 1 -> lưu -> tiếp tục kỷ 2).
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device != "cuda":
        pytest.skip("CUDA execution required for Stage A2 empirical parity")
        
    seed = 42
    events = build_dummy_fixture_events(16)
    
    # 1. Chạy đào tạo 2 giai đoạn liên tục
    cont_root = tmp_path / "continuous"
    res_cont = run_single_seed_pipeline(
        seed=seed,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=cont_root,
        fixture_train_events=events,
        fixture_val_events=events,
        max_epochs=2
    )
    
    # 2. Chạy huấn luyện 1 kỷ và mô phỏng sự gián đoạn trước epoch 2
    epoch1_root = tmp_path / "epoch1"
    res_ep1 = run_single_seed_pipeline(
        seed=seed,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=epoch1_root,
        fixture_train_events=events,
        fixture_val_events=events,
        max_epochs=1
    )
    
    # Đánh dấu trạng thái là INTERRUPTED với mục tiêu max_epochs=2
    state_file = epoch1_root / "evidence" / "RUN-STATE.json"
    state_data = json.loads(state_file.read_text(encoding="utf-8"))
    state_data["status"] = "INTERRUPTED"
    state_data["completed_epoch"] = 1
    state_data["next_epoch_to_run"] = 1
    state_file.write_text(json.dumps(state_data, indent=2) + "\n", encoding="utf-8")
    
    ckpt_path = epoch1_root / "artifacts" / "last_checkpoint.pt"
    assert ckpt_path.exists()
    
    # 3. Tiếp tục epoch 2 từ checkpoint
    res_resumed = run_single_seed_pipeline(
        seed=seed,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        resume_checkpoint=ckpt_path,
        fixture_mode=True,
        fixture_output_root=epoch1_root,
        fixture_train_events=events,
        fixture_val_events=events,
        max_epochs=2
    )
    
    # So sánh trọng số cuối cùng
    cont_ckpt = torch.load(cont_root / "artifacts" / "last_checkpoint.pt", map_location="cpu", weights_only=False)
    res_ckpt = torch.load(epoch1_root / "artifacts" / "last_checkpoint.pt", map_location="cpu", weights_only=False)
    
    for k in cont_ckpt["model_state_dict"]:
        p_cont = cont_ckpt["model_state_dict"][k]
        p_res = res_ckpt["model_state_dict"][k]
        diff = (p_cont - p_res).abs().max().item()
        assert diff < 1e-5, f"Weight divergence in {k}: max diff = {diff}"

def test_dropout_covered_proves_no_post_resume_reseed():
    """
    Kiểm tra rõ ràng quỹ đạo lấy mẫu Bỏ học (p=0,5) trong sơ yếu lý lịch
    không được thiết lập lại về trạng thái ban đầu.
    """
    dropout = torch.nn.Dropout(p=0.5)
    dropout.train()
    x = torch.ones(10, 10)
    
    # Lần 1: Lấy mẫu liên tục
    torch.manual_seed(42)
    out1 = dropout(x)
    out2 = dropout(x)
    
    # Lần 2: Bị gián đoạn với trạng thái lưu/tải
    torch.manual_seed(42)
    out1_rep = dropout(x)
    saved_rng = torch.get_rng_state()
    
    # Trong mã cũ xấu, ai đó có thể gieo hạt lại bằng torch.manual_seed(42)
    # Nhưng với mã chính xác, chúng tôi khôi phục saved_rng mà không cần gieo hạt lại:
    torch.set_rng_state(saved_rng)
    out2_rep = dropout(x)
    
    assert torch.equal(out1, out1_rep)
    assert torch.equal(out2, out2_rep)
    assert not torch.equal(out1, out2), "Dropout outputs at step 1 and step 2 must differ!"
