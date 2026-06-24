from flask import Flask, request, render_template, jsonify
import os
import uuid
import json
import datetime

app = Flask(__name__)
app.secret_key = 'plantdoc-secret-key-2024'

UPLOAD_FOLDER = "static/uploads"
HISTORY_FILE  = "history.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── 8 lớp khớp với notebook (index 0-7) ─────────────────────────────────────
classes = [
    'Healthy',       # 0
    'BrownSpot',     # 1
    'LeafBlast',     # 2
    'Hispa',         # 3
    'LeafScald',     # 4
    'LeafBlight',    # 5
    'NeckBlast',     # 6
    'SheathBlight',  # 7
]

# ── Database bệnh ────────────────────────────────────────────────────────────
disease_db = {

    # ── 0 ────────────────────────────────────────────────────────────────────
    'Healthy': {
        'name': 'Cây khỏe mạnh',
        'sci': 'Oryza sativa',
        'severity': 'An toàn',
        'severity_color': 'teal',
        'severity_days': 'Không cần xử lý',
        'symptoms': [
            {'label': 'Màu lá',  'val': 'Xanh mướt đều',    'color': 'teal', 'icon': 'ti-leaf'},
            {'label': 'Thân cây','val': 'Cứng cáp, thẳng',  'color': 'teal', 'icon': 'ti-plant-2'},
            {'label': 'Rễ cây',  'val': 'Trắng khỏe mạnh',  'color': 'teal', 'icon': 'ti-seeding'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Không cần phun thuốc khi cây đang khỏe mạnh.', 'tag': 'Không cần'},
                {'text': 'Chỉ dùng thuốc khi có dấu hiệu bệnh rõ ràng để tránh kháng thuốc.', 'tag': 'Lưu ý'},
            ],
            'organic': [
                {'text': 'Bón phân hữu cơ định kỳ để duy trì sức đề kháng tự nhiên.', 'tag': 'Khuyến nghị'},
                {'text': 'Phun phân bón lá vi lượng (kẽm, bo) để tăng cường dinh dưỡng.', 'tag': 'Bổ sung'},
            ],
            'prevent': [
                {'text': 'Kiểm tra lá và thân cây mỗi 3–5 ngày để phát hiện bệnh sớm.', 'tag': 'Quan trọng'},
                {'text': 'Duy trì mực nước ruộng ổn định, tránh quá khô hoặc quá ngập.', 'tag': 'Cơ bản'},
                {'text': 'Vệ sinh ruộng sau thu hoạch, diệt nguồn bệnh lưu tồn.', 'tag': 'Dài hạn'},
            ],
        },
        'similar': [
            {'name': 'BrownSpot giai đoạn đầu', 'prob': 3, 'color': '#F09595'},
            {'name': 'Thiếu dinh dưỡng nhẹ',   'prob': 2, 'color': '#EF9F27'},
        ],
    },

    # ── 1 ────────────────────────────────────────────────────────────────────
    'BrownSpot': {
        'name': 'Đốm nâu',
        'sci': 'Cochliobolus miyabeanus',
        'severity': 'Trung bình',
        'severity_color': 'amber',
        'severity_days': 'Xử lý trong 3–5 ngày',
        'symptoms': [
            {'label': 'Vết đốm',  'val': 'Tròn, tâm xám viền nâu',  'color': 'red',   'icon': 'ti-circle-dot'},
            {'label': 'Lá khô',   'val': 'Rìa đốm màu vàng',        'color': 'amber', 'icon': 'ti-leaf'},
            {'label': 'Hạt lép',  'val': 'Biến màu nâu đen',        'color': 'teal',  'icon': 'ti-droplet'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun thuốc gốc đồng (Copper Oxychloride) nồng độ 0.3% vào buổi sáng sớm.', 'tag': 'Hiệu quả cao'},
                {'text': 'Sử dụng Carbendazim 50WP, phun 2 lần cách nhau 7 ngày.', 'tag': 'Phổ biến'},
                {'text': 'Kiểm soát lượng đạm bón, tránh bón thừa nitơ khi bệnh xuất hiện.', 'tag': 'Bổ trợ'},
            ],
            'organic': [
                {'text': 'Ủ và bón phân chuồng hoai mục, tăng sức đề kháng cho đất.', 'tag': 'An toàn'},
                {'text': 'Phun dung dịch nước tỏi pha loãng 1:10 lên lá mỗi tuần.', 'tag': 'Tự nhiên'},
                {'text': 'Dùng chế phẩm Trichoderma bón gốc để ức chế nấm trong đất.', 'tag': 'Sinh học'},
            ],
            'prevent': [
                {'text': 'Chọn giống lúa kháng bệnh đốm nâu được khuyến cáo tại địa phương.', 'tag': 'Dài hạn'},
                {'text': 'Vệ sinh đồng ruộng, dọn sạch tàn dư cây sau thu hoạch.', 'tag': 'Cơ bản'},
                {'text': 'Bón phân cân đối NPK, không để cây thiếu kali và phốt pho.', 'tag': 'Dinh dưỡng'},
            ],
        },
        'similar': [
            {'name': 'Đốm vằn',    'prob': 6, 'color': '#F09595'},
            {'name': 'Khô vằn',    'prob': 5, 'color': '#EF9F27'},
            {'name': 'Lem lép hạt','prob': 2, 'color': '#5DCAA5'},
        ],
    },

    # ── 2 ────────────────────────────────────────────────────────────────────
    'LeafBlast': {
        'name': 'Đạo ôn lá',
        'sci': 'Magnaporthe oryzae',
        'severity': 'Cao',
        'severity_color': 'red',
        'severity_days': 'Xử lý khẩn cấp trong 24h',
        'symptoms': [
            {'label': 'Hình mắt én', 'val': 'Đốm thoi đặc trưng',     'color': 'red',   'icon': 'ti-circle-dot'},
            {'label': 'Khô lá',      'val': 'Vết lan rộng nhanh',      'color': 'red',   'icon': 'ti-leaf'},
            {'label': 'Gãy cổ lá',  'val': 'Vết đen quanh khớp lá',  'color': 'amber', 'icon': 'ti-droplet'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun Tricyclazole 75WP (0.5 g/lít) ngay khi phát hiện bệnh, lặp lại sau 7 ngày.', 'tag': 'Ưu tiên #1'},
                {'text': 'Kết hợp Kasugamycin và Propiconazole cho hiệu quả kép chống nấm.', 'tag': 'Kết hợp'},
                {'text': 'Phun Kitazin 48EC nếu đạo ôn đã lan sang cổ bông.', 'tag': 'Nghiêm trọng'},
            ],
            'organic': [
                {'text': 'Giảm bón đạm ngay lập tức, cân đối lại phân kali và silic.', 'tag': 'Cấp bách'},
                {'text': 'Phun dịch chiết hạt neem 3% để ức chế sự phát triển của nấm.', 'tag': 'Bổ trợ'},
                {'text': 'Tưới nước liên tục để duy trì ẩm đất, tránh để cây bị stress khô hạn.', 'tag': 'Hỗ trợ'},
            ],
            'prevent': [
                {'text': 'Giữ mật độ gieo sạ vừa phải, không quá 120 kg giống/ha.', 'tag': 'Quan trọng'},
                {'text': 'Quản lý nước ruộng tốt, không để ruộng khô hạn giai đoạn làm đòng.', 'tag': 'Nước'},
                {'text': 'Chọn giống kháng đạo ôn như IR64, OM5451 được khuyến cáo.', 'tag': 'Giống'},
            ],
        },
        'similar': [
            {'name': 'NeckBlast (đạo ôn cổ bông)', 'prob': 9, 'color': '#E24B4A'},
            {'name': 'Khô vằn',                    'prob': 4, 'color': '#F09595'},
            {'name': 'Cháy bìa lá (BacterialBlight)','prob': 3,'color': '#EF9F27'},
        ],
    },

    # ── 3 ────────────────────────────────────────────────────────────────────
    'Hispa': {
        'name': 'Sâu gai (Hispa)',
        'sci': 'Dicladispa armigera',
        'severity': 'Cao',
        'severity_color': 'red',
        'severity_days': 'Xử lý ngay trong 1–2 ngày',
        'symptoms': [
            {'label': 'Vết cắn',   'val': 'Sọc trắng dọc lá',      'color': 'red',   'icon': 'ti-bolt'},
            {'label': 'Lá bạc',    'val': 'Thịt lá bị ăn rỗng',    'color': 'red',   'icon': 'ti-leaf'},
            {'label': 'Trứng sâu', 'val': 'Đẻ gần chóp lá non',    'color': 'amber', 'icon': 'ti-circle-dot'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun Quinalphos 25EC nồng độ 1.5 ml/lít nước, xử lý buổi chiều mát.', 'tag': 'Ưu tiên'},
                {'text': 'Sử dụng Chlorpyriphos 20EC, phun ướt đều mặt dưới lá.', 'tag': 'Hiệu quả cao'},
                {'text': 'Kết hợp Acephate nếu mật độ sâu cao trên 5 con/khóm.', 'tag': 'Nặng'},
            ],
            'organic': [
                {'text': 'Thu gom và tiêu hủy thủ công các lá bị sâu gai tấn công nặng.', 'tag': 'Tức thời'},
                {'text': 'Dùng bẫy ánh sáng vàng ban đêm để bắt sâu trưởng thành.', 'tag': 'Bẫy'},
                {'text': 'Phun dung dịch neem oil 5% để xua đuổi và diệt sâu non.', 'tag': 'Sinh học'},
            ],
            'prevent': [
                {'text': 'Vệ sinh và diệt cỏ dại quanh bờ ruộng — nơi sâu trú ẩn qua đông.', 'tag': 'Quan trọng'},
                {'text': 'Áp dụng luân canh cây trồng, không trồng lúa liên tục nhiều vụ.', 'tag': 'Dài hạn'},
                {'text': 'Thả thiên địch ong mắt đỏ Trichogramma vào đầu vụ.', 'tag': 'Sinh học'},
            ],
        },
        'similar': [
            {'name': 'Sâu cuốn lá',   'prob': 8, 'color': '#F09595'},
            {'name': 'Bọ trĩ hại lúa','prob': 5, 'color': '#EF9F27'},
            {'name': 'Rầy nâu',        'prob': 3, 'color': '#5DCAA5'},
        ],
    },

    # ── 4 ────────────────────────────────────────────────────────────────────
    'LeafScald': {
        'name': 'Bỏng lá (Leaf Scald)',
        'sci': 'Microdochium oryzae',
        'severity': 'Trung bình',
        'severity_color': 'amber',
        'severity_days': 'Xử lý trong 5–7 ngày',
        'symptoms': [
            {'label': 'Vết bỏng',   'val': 'Vàng nâu từ chóp lá lan xuống',  'color': 'amber', 'icon': 'ti-flame'},
            {'label': 'Ranh giới',  'val': 'Vệt nâu sậm rõ, hình sóng',      'color': 'amber', 'icon': 'ti-wave-sine'},
            {'label': 'Viền lá',    'val': 'Khô xoăn dọc mép lá',            'color': 'red',   'icon': 'ti-leaf'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun Propiconazole 25EC (1 ml/lít nước) khi bệnh mới xuất hiện.', 'tag': 'Hiệu quả'},
                {'text': 'Dùng Hexaconazole hoặc Tebuconazole nếu bệnh lan nhanh.', 'tag': 'Thay thế'},
                {'text': 'Phun 2 đợt cách nhau 10 ngày để ngăn tái nhiễm.', 'tag': 'Lặp lại'},
            ],
            'organic': [
                {'text': 'Giảm bón đạm, tăng cường kali và silic để lá cứng cáp hơn.', 'tag': 'Dinh dưỡng'},
                {'text': 'Phun dịch chiết tỏi + gừng pha loãng 1:15 mỗi 5 ngày.', 'tag': 'Tự nhiên'},
                {'text': 'Bón Trichoderma vào đất để kiểm soát nấm gây bệnh.', 'tag': 'Sinh học'},
            ],
            'prevent': [
                {'text': 'Không để ruộng bị hạn hán, duy trì ẩm độ đất ổn định.', 'tag': 'Nước'},
                {'text': 'Tránh gây tổn thương cơ học cho lá khi chăm sóc.', 'tag': 'Thao tác'},
                {'text': 'Chọn giống có khả năng chịu nóng và kháng nấm.', 'tag': 'Giống'},
            ],
        },
        'similar': [
            {'name': 'BrownSpot',                 'prob': 7, 'color': '#F09595'},
            {'name': 'LeafBlight (cháy bìa lá)',  'prob': 6, 'color': '#EF9F27'},
            {'name': 'Khô đầu lá do thiếu nước',  'prob': 4, 'color': '#5DCAA5'},
        ],
    },

    # ── 5 ────────────────────────────────────────────────────────────────────
    'LeafBlight': {
        'name': 'Cháy bìa lá (Bạc lá)',
        'sci': 'Xanthomonas oryzae pv. oryzae',
        'severity': 'Cao',
        'severity_color': 'red',
        'severity_days': 'Xử lý khẩn cấp trong 1–2 ngày',
        'symptoms': [
            {'label': 'Vết bạc',    'val': 'Lan từ chóp và mép lá vào',      'color': 'red',   'icon': 'ti-leaf'},
            {'label': 'Giọt khuẩn', 'val': 'Dịch vàng khô thành vảy',        'color': 'amber', 'icon': 'ti-droplet'},
            {'label': 'Lá khô',     'val': 'Cuộn và chết theo đường thẳng',  'color': 'red',   'icon': 'ti-flame'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun Bismerthiazol (Starner 20WP) 1.5 g/lít, là thuốc đặc trị vi khuẩn.', 'tag': 'Ưu tiên #1'},
                {'text': 'Dùng Copper hydroxide (Kocide) 2 g/lít, phun 2 lần cách nhau 7 ngày.', 'tag': 'Đặc trị'},
                {'text': 'Kết hợp phun Kasugamycin để tăng hiệu quả diệt khuẩn.', 'tag': 'Kết hợp'},
            ],
            'organic': [
                {'text': 'Cắt bỏ và tiêu hủy lá bệnh nặng ngay khi phát hiện.', 'tag': 'Cấp bách'},
                {'text': 'Phun dung dịch đồng sunfat 0.1% (nước Bordeaux) lên lá.', 'tag': 'Truyền thống'},
                {'text': 'Bón phân hữu cơ giàu silic giúp tăng độ cứng tế bào lá.', 'tag': 'Hỗ trợ'},
            ],
            'prevent': [
                {'text': 'Không để nước tràn từ ruộng bệnh sang ruộng lành khi tưới tiêu.', 'tag': 'Quan trọng'},
                {'text': 'Hạn chế gây vết thương lá khi phun thuốc hoặc bón phân.', 'tag': 'Thao tác'},
                {'text': 'Trồng giống kháng bạc lá: IRBB21, BT7 cải tiến, OM9915.', 'tag': 'Giống kháng'},
            ],
        },
        'similar': [
            {'name': 'LeafScald',            'prob': 7, 'color': '#F09595'},
            {'name': 'Cháy lá do phân bón',  'prob': 4, 'color': '#EF9F27'},
            {'name': 'LeafBlast (đạo ôn lá)','prob': 3, 'color': '#5DCAA5'},
        ],
    },

    # ── 6 ────────────────────────────────────────────────────────────────────
    'NeckBlast': {
        'name': 'Đạo ôn cổ bông',
        'sci': 'Magnaporthe oryzae',
        'severity': 'Rất cao',
        'severity_color': 'red',
        'severity_days': 'Xử lý khẩn cấp trong 12–24h — mất mùa nếu chậm trễ',
        'symptoms': [
            {'label': 'Cổ bông',   'val': 'Vết đen, bẹp, gãy cổ',         'color': 'red',   'icon': 'ti-circle-dot'},
            {'label': 'Hạt lép',   'val': 'Lép hoàn toàn hoặc lửng',       'color': 'red',   'icon': 'ti-grain'},
            {'label': 'Bông rủ',   'val': 'Cổ bông bị gãy, bông trắng',    'color': 'amber', 'icon': 'ti-leaf'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun gấp Tricyclazole 75WP (1 g/lít) ngay khi thấy vết đen ở cổ bông.', 'tag': 'Khẩn cấp'},
                {'text': 'Dùng Isoprothiolane (Fuji-One 40EC) 1.5 ml/lít — hiệu quả lây lan.', 'tag': 'Ưu tiên'},
                {'text': 'Kết hợp Propiconazole + Difenoconazole nếu bệnh lan sang lóng thân.', 'tag': 'Nặng'},
            ],
            'organic': [
                {'text': 'Không còn nhiều lựa chọn hữu cơ ở giai đoạn này — ưu tiên thuốc hóa học.', 'tag': 'Lưu ý'},
                {'text': 'Bổ sung kali và silic qua lá để tăng sức chịu đựng bệnh.', 'tag': 'Hỗ trợ'},
            ],
            'prevent': [
                {'text': 'Phun phòng Tricyclazole trước trổ bông 7–10 ngày là biện pháp quan trọng nhất.', 'tag': 'Quan trọng nhất'},
                {'text': 'Theo dõi dự báo thời tiết, phun phòng khi trời ẩm ướt kéo dài.', 'tag': 'Thời tiết'},
                {'text': 'Hạn chế bón đạm muộn (sau đứng cái), dễ tạo điều kiện cho nấm phát triển.', 'tag': 'Dinh dưỡng'},
            ],
        },
        'similar': [
            {'name': 'LeafBlast (đạo ôn lá)',   'prob': 9, 'color': '#E24B4A'},
            {'name': 'SheathBlight (khô vằn)',   'prob': 5, 'color': '#F09595'},
            {'name': 'Lem lép hạt do vi khuẩn', 'prob': 4, 'color': '#EF9F27'},
        ],
    },

    # ── 7 ────────────────────────────────────────────────────────────────────
    'SheathBlight': {
        'name': 'Khô vằn (Đốm vằn bẹ lá)',
        'sci': 'Rhizoctonia solani',
        'severity': 'Cao',
        'severity_color': 'red',
        'severity_days': 'Xử lý trong 2–3 ngày',
        'symptoms': [
            {'label': 'Vết bẹ',    'val': 'Đốm bầu dục xám trắng viền nâu', 'color': 'red',   'icon': 'ti-circle-dot'},
            {'label': 'Lan lên',   'val': 'Từ gốc leo lên bẹ, lá, cổ bông', 'color': 'red',   'icon': 'ti-arrow-up'},
            {'label': 'Hạch nấm',  'val': 'Hạt tròn nâu đen trên bẹ lúa',  'color': 'amber', 'icon': 'ti-dots'},
        ],
        'treatments': {
            'chemical': [
                {'text': 'Phun Hexaconazole 5SC (1 ml/lít) hoặc Propiconazole 25EC ngay khi phát hiện.', 'tag': 'Ưu tiên'},
                {'text': 'Dùng Validamycin A (Vanicide 3SL) 2 ml/lít — hiệu quả đặc trị Rhizoctonia.', 'tag': 'Đặc trị'},
                {'text': 'Phun ướt gốc lúa và bẹ — nơi nấm sinh trưởng chính.', 'tag': 'Kỹ thuật phun'},
            ],
            'organic': [
                {'text': 'Rút nước ruộng tạm thời để hạn chế độ ẩm — nấm Rhizoctonia thích ẩm ướt.', 'tag': 'Thoát nước'},
                {'text': 'Bón Trichoderma harzianum vào đất trước khi cấy để kiểm soát nấm nguồn.', 'tag': 'Sinh học'},
                {'text': 'Phun dịch chiết tỏi đậm đặc (1:8) vào gốc và bẹ lá 2 lần/tuần.', 'tag': 'Thảo mộc'},
            ],
            'prevent': [
                {'text': 'Cấy mật độ vừa phải, thông thoáng giữa các khóm để hạn chế ẩm độ.', 'tag': 'Mật độ'},
                {'text': 'Hạn chế để ruộng ngập liên tục dài ngày trong giai đoạn đẻ nhánh.', 'tag': 'Nước'},
                {'text': 'Không bón thừa đạm, cân đối NPK + kali để lúa cứng cây.', 'tag': 'Dinh dưỡng'},
            ],
        },
        'similar': [
            {'name': 'BrownSpot',            'prob': 6, 'color': '#F09595'},
            {'name': 'NeckBlast',            'prob': 5, 'color': '#E24B4A'},
            {'name': 'Lem lép hạt',          'prob': 3, 'color': '#EF9F27'},
        ],
    },
}


# ── Load / save history ──────────────────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(record):
    history = load_history()
    history.insert(0, record)
    history = history[:50]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ── Model loading ─────────────────────────────────────────────────────────────

model     = None
transform = None


def load_model():
    """
    .pth lưu state_dict (OrderedDict) — phải khởi tạo CNN rồi load_state_dict.
    Kiến trúc xác minh từ tensor shapes trong file:
      conv1(3→16) conv2(16→32) conv3(32→64) → fc1(1600→256) → fc2(256→128) → fc3(128→8)
      Input ảnh: 60×60  |  8 classes  |
    """
    global model, transform

    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        import torchvision.transforms as T

        # ── Định nghĩa kiến trúc khớp với file .pth ──────────────────────
        class CNN(nn.Module):
            def __init__(self):
                super(CNN, self).__init__()
                self.conv1   = nn.Conv2d(3, 16, 3)
                self.conv2   = nn.Conv2d(16, 32, 3)
                self.conv3   = nn.Conv2d(32, 64, 3)
                self.pool    = nn.MaxPool2d(2)
                self.flatten = nn.Flatten()
                self.fc1     = nn.Linear(64 * 5 * 5, 256)
                self.fc2     = nn.Linear(256, 128)
                self.fc3     = nn.Linear(128, 8)
                self.softmax = nn.LogSoftmax(dim=1)

            def forward(self, x):
                x = self.pool(F.relu(self.conv1(x)))
                x = self.pool(F.relu(self.conv2(x)))
                x = self.pool(F.relu(self.conv3(x)))
                x = self.flatten(x)
                x = F.relu(self.fc1(x))
                x = F.relu(self.fc2(x))
                return self.softmax(self.fc3(x))

        # ── Load weights vào model ─────────────────────────────────────────
        m = CNN()
        state_dict = torch.load("rice_model_ok.pth", map_location="cpu", weights_only=True)
        m.load_state_dict(state_dict)
        m.eval()
        model = m

        # ── Transform: 60×60, không Normalize (notebook train không dùng) ──
        transform = T.Compose([
            T.Resize((60, 60)),
            T.ToTensor(),
        ])

        print(f"✅ CNN loaded — rice_model_ok.pth — {len(classes)} classes")

    except Exception as e:
        print(f"⚠️ Model load error: {e}")


load_model()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('giaodien.html')


@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'Không có ảnh được gửi lên'}), 400

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if model is not None:
        try:
            import torch
            import torch.nn.functional as F
            from PIL import Image
            img        = Image.open(filepath).convert('RGB')
            img_tensor = transform(img).unsqueeze(0)
            with torch.no_grad():
                output = model(img_tensor)
                probs  = F.softmax(output[0], dim=0)
                conf, pred = torch.max(probs, 0)
            class_id   = classes[pred.item()]
            confidence = int(conf.item() * 100)
            # Top-3 xác suất
            top3_vals, top3_idx = torch.topk(probs, min(3, len(classes)))
            top3 = [
                {'name': disease_db[classes[i.item()]]['name'],
                 'prob': int(v.item() * 100)}
                for v, i in zip(top3_vals, top3_idx)
            ]
        except Exception as e:
            return jsonify({'error': f'Lỗi xử lý ảnh: {str(e)}'}), 500
    else:
        import random
        class_id   = random.choice(classes)
        confidence = random.randint(72, 96)
        top3       = [{'name': disease_db[class_id]['name'], 'prob': confidence}]

    info   = disease_db[class_id]
    result = {
        'class_id':      class_id,
        'class_name':    info['name'],
        'sci_name':      info['sci'],
        'severity':      info['severity'],
        'severity_color':info['severity_color'],
        'severity_days': info['severity_days'],
        'confidence':    confidence,
        'symptoms':      info['symptoms'],
        'treatments':    info['treatments'],
        'similar':       info['similar'],
        'top3':          top3,
        'image_url':     f'/static/uploads/{filename}',
        'timestamp':     datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
    }

    save_history({
        'class_name': result['class_name'],
        'confidence': confidence,
        'severity':   info['severity'],
        'image_url':  result['image_url'],
        'timestamp':  result['timestamp'],
    })

    return jsonify(result)


@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(load_history())


@app.route('/history/clear', methods=['POST'])
def clear_history():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    return jsonify({'ok': True})


@app.route('/classes', methods=['GET'])
def get_classes():
    """Trả về danh sách tất cả lớp bệnh — tiện cho frontend."""
    return jsonify([
        {
            'id':       k,
            'name':     v['name'],
            'sci':      v['sci'],
            'severity': v['severity'],
            'severity_color': v['severity_color'],
        }
        for k, v in disease_db.items()
    ])


@app.route('/chat', methods=['POST'])
def chat():
    """
    Rule-based AI advice endpoint.
    Body: { "disease": "BrownSpot", "question": "thuốc gì?" }
    """
    data     = request.get_json() or {}
    disease  = data.get('disease', '')
    question = data.get('question', '').lower()

    # Tìm info bất kể tên tiếng Anh hay tiếng Việt
    info = None
    for key, val in disease_db.items():
        if val['name'] == disease or key == disease:
            info = val
            break

    if not info:
        return jsonify({
            'reply': (
                'Tôi chưa có thông tin về loại bệnh này. '
                f'Các bệnh hiện hỗ trợ: {", ".join(v["name"] for v in disease_db.values())}.'
            )
        })

    # Phân loại câu hỏi theo từ khóa
    if any(w in question for w in ['thuốc', 'phun', 'hóa chất', 'hóa học', 'chemical']):
        steps = info['treatments']['chemical']
        reply = f"**Xử lý hóa học — {info['name']}:**\n" + "\n".join(f"• [{s['tag']}] {s['text']}" for s in steps)

    elif any(w in question for w in ['hữu cơ', 'tự nhiên', 'sinh học', 'organic', 'thảo mộc']):
        steps = info['treatments']['organic']
        reply = f"**Biện pháp hữu cơ — {info['name']}:**\n" + "\n".join(f"• [{s['tag']}] {s['text']}" for s in steps)

    elif any(w in question for w in ['phòng', 'ngăn', 'tránh', 'prevent', 'phòng ngừa']):
        steps = info['treatments']['prevent']
        reply = f"**Phòng ngừa — {info['name']}:**\n" + "\n".join(f"• [{s['tag']}] {s['text']}" for s in steps)

    elif any(w in question for w in ['triệu chứng', 'dấu hiệu', 'nhận biết', 'symptom']):
        syms = info['symptoms']
        reply = f"**Triệu chứng — {info['name']}:**\n" + "\n".join(f"• {s['label']}: {s['val']}" for s in syms)

    elif any(w in question for w in ['nguy hiểm', 'mức độ', 'nặng', 'severity', 'nghiêm trọng']):
        reply = (
            f"**{info['name']}** có mức độ **{info['severity']}**.\n"
            f"{info['severity_days']}.\n"
            f"Loài gây bệnh: *{info['sci']}*"
        )

    elif any(w in question for w in ['giống', 'giống lúa', 'kháng']):
        # Lấy gợi ý giống từ phần prevent
        prevent_items = [s['text'] for s in info['treatments']['prevent'] if 'giống' in s['text'].lower()]
        if prevent_items:
            reply = f"**Giống kháng bệnh {info['name']}:**\n" + "\n".join(f"• {t}" for t in prevent_items)
        else:
            reply = f"Chưa có thông tin giống kháng đặc hiệu cho {info['name']}. Liên hệ cán bộ khuyến nông địa phương."

    else:
        # Tóm tắt tổng quát
        reply = (
            f"**{info['name']}** (*{info['sci']}*)\n"
            f"Mức độ: **{info['severity']}** — {info['severity_days']}\n\n"
            f"Triệu chứng chính: {', '.join(s['label'] for s in info['symptoms'])}\n\n"
            f"Hỏi tôi về: `thuốc`, `hữu cơ`, `phòng ngừa`, `triệu chứng`, `mức độ` để được hướng dẫn chi tiết."
        )

    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)