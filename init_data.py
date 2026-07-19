from app import db, Disease

def insert_disease_data():
    data = [
        ("Aphid", "喷洒吡虫啉等低毒杀虫剂，及时清除虫源；种植抗蚜品种。"),
        ("Black Rust", "可使用三唑类杀菌剂如戊唑醇，注意轮作换茬。"),
        ("Blast", "改善田间通风透光，使用稻瘟灵、三环唑等杀菌剂。"),
        ("Brown Rust", "喷洒烯唑醇，清除病株，减少田间湿度。"),
        ("Common Root Rot", "合理轮作，清除病残体，可用多菌灵处理种子。"),
        ("Fusarium Head Blight", "开花期避免灌水，喷洒多菌灵、福美双等。"),
        ("Healthy", "无明显病害，注意田间管理，保持作物健康。"),
        ("Leaf Blight", "喷洒代森锰锌、甲基托布津，注意通风。"),
        ("Mildew", "用三唑酮、粉锈宁等，控制温湿度，增强作物抗性。"),
        ("Mite", "喷施阿维菌素，减少杂草虫源，合理密植。"),
        ("Septoria", "及时清除病叶，施用苯醚甲环唑类药剂控制扩散。"),
        ("Smut", "播种前种子拌种处理，避免高温高湿环境。"),
        ("Stem fly", "播种前处理种子，苗期喷施杀虫剂如辛硫磷。"),
        ("Tan spot", "适当轮作，施用叶面杀菌剂如多菌灵防治。"),
        ("Yellow Rust", "用烯唑醇、戊唑醇防治，加强巡查及时发现。")
    ]
    for name, suggestion in data:
        if not Disease.query.filter_by(name=name).first():
            db.session.add(Disease(name=name, suggestion=suggestion))
    db.session.commit()
    print("✅ 已添加所有病害防治信息")

if __name__ == '__main__':
    insert_disease_data()
