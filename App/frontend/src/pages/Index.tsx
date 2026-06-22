import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Brain, Pill, BookOpen, ArrowRight, Zap } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import DiseaseCard from '@/components/DiseaseCard';
import client from '@/lib/client';

const Index = () => {
  const navigate = useNavigate();
  const [diseases, setDiseases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchName, setSearchName] = useState('');
  const [searchSymptoms, setSearchSymptoms] = useState('');

  useEffect(() => {
    const fetchDiseases = async () => {
      try {
        const response = await client.entities.diseases.query({ limit: 1000 });
        setDiseases(response.data?.items || []);
      } catch (err) {
        console.error('Failed to fetch diseases:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDiseases();
  }, []);

  const handlePredict = () => {
    const params = new URLSearchParams();
    if (searchName) params.set('name', searchName);
    if (searchSymptoms) params.set('symptoms', searchSymptoms);
    navigate(`/predict?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-700 via-blue-600 to-blue-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.04%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur border border-white/20 rounded-full px-4 py-1.5 text-sm mb-6">
                <Zap className="h-4 w-4 text-amber-300" />
                <span>AI Y tế thế hệ mới 2026</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-5">
                Dự Đoán Và Gợi Ý Thuốc{' '}
                <span className="text-blue-200">Theo Bệnh Lý</span> Bằng AI
              </h1>
              <p className="text-blue-100 text-lg leading-relaxed mb-8">
                Hệ thống AI tiên tiến phân tích triệu chứng, dự đoán bệnh lý và đề xuất phác đồ điều trị phù hợp — nhanh chóng, chính xác và đáng tin cậy.
              </p>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => navigate('/predict')}
                  className="h-12 px-7 bg-white text-blue-700 font-semibold rounded-xl hover:bg-blue-50 transition-colors flex items-center gap-2"
                >
                  Tra cứu ngay <ArrowRight className="h-5 w-5" />
                </button>
                <button
                  onClick={() => navigate('/search')}
                  className="h-12 px-7 border border-white/30 text-white font-medium rounded-xl hover:bg-white/10 transition-colors flex items-center gap-2"
                >
                  <BookOpen className="h-5 w-5" /> Tìm hiểu thêm
                </button>
              </div>
              <div className="flex flex-wrap gap-6 mt-10">
                {[['10.000+', 'Lượt tra cứu'], ['1.000+', 'Loại thuốc'], ['500+', 'Bệnh lý'], ['98%', 'Độ chính xác']].map(([n, l]) => (
                  <div key={l}>
                    <p className="text-2xl font-bold">{n}</p>
                    <p className="text-blue-200 text-sm">{l}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="hidden md:grid grid-cols-2 gap-4">
              {[
                { icon: '🧠', title: 'AI Dự đoán', desc: 'Phân tích triệu chứng thông minh', color: 'from-blue-500/20 to-blue-400/10' },
                { icon: '💊', title: 'Gợi ý thuốc', desc: '1.000+ loại thuốc trong CSDL', color: 'from-emerald-500/20 to-emerald-400/10' },
                { icon: '🔬', title: 'Kiến thức y khoa', desc: 'Thông tin bệnh lý từ chuyên gia', color: 'from-amber-500/20 to-amber-400/10' },
                { icon: '🏥', title: 'An toàn & Tin cậy', desc: 'Được kiểm duyệt bởi bác sĩ', color: 'from-purple-500/20 to-purple-400/10' },
              ].map((card) => (
                <div key={card.title} className={`bg-gradient-to-br ${card.color} backdrop-blur border border-white/20 rounded-2xl p-5`}>
                  <div className="text-3xl mb-3">{card.icon}</div>
                  <h3 className="font-semibold text-white text-sm">{card.title}</h3>
                  <p className="text-blue-200 text-xs mt-1">{card.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Search Box */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6 mb-12 relative z-10">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6 md:p-8">
          <h2 className="text-xl font-bold text-slate-900 mb-2">Dự đoán bệnh từ triệu chứng</h2>
          <p className="text-slate-500 text-sm mb-5">Nhập tên bệnh hoặc mô tả triệu chứng để nhận gợi ý từ AI</p>
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="Nhập tên bệnh (vd: Tiểu đường, Cảm cúm...)"
                className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                value={searchSymptoms}
                onChange={(e) => setSearchSymptoms(e.target.value)}
                placeholder="Mô tả triệu chứng (vd: Sốt, Ho, Đau đầu...)"
                className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handlePredict}
              className="h-12 px-8 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              <Brain className="h-5 w-5" /> Dự đoán AI
            </button>
          </div>
        </div>
      </section>

      {/* Popular Diseases */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-14">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Bệnh lý phổ biến</h2>
          <button
            onClick={() => navigate('/search')}
            className="text-blue-600 text-sm font-medium flex items-center gap-1 hover:gap-2 transition-all"
          >
            Xem tất cả <ArrowRight className="h-4 w-4" />
          </button>
        </div>
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {diseases.slice(0, 6).map((disease) => (
              <DiseaseCard key={disease.id} disease={disease} />
            ))}
          </div>
        )}
      </section>

      {/* Features */}
      <section className="bg-white py-14">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Tính năng nổi bật</h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              MediPredict cung cấp bộ công cụ AI y tế toàn diện, giúp bạn hiểu rõ tình trạng sức khỏe
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: <Brain className="h-7 w-7 text-blue-600" />, bg: 'bg-blue-50', title: 'Dự đoán AI thông minh', desc: 'Thuật toán AI tiên tiến phân tích hơn 200 triệu chứng, cho kết quả dự đoán chính xác 98%' },
              { icon: <Pill className="h-7 w-7 text-emerald-600" />, bg: 'bg-emerald-50', title: 'Gợi ý thuốc cá nhân hóa', desc: 'Đề xuất phác đồ thuốc phù hợp với từng bệnh nhân, xem xét dị ứng và tương tác thuốc' },
              { icon: <BookOpen className="h-7 w-7 text-amber-600" />, bg: 'bg-amber-50', title: 'Kiến thức y khoa chuyên sâu', desc: 'Kho tàng thông tin y khoa cập nhật liên tục, được kiểm duyệt bởi đội ngũ bác sĩ chuyên khoa' },
            ].map((f) => (
              <div key={f.title} className="bg-slate-50 rounded-2xl p-7 border border-slate-200 hover:shadow-md transition-shadow">
                <div className={`w-14 h-14 ${f.bg} rounded-xl flex items-center justify-center mb-5`}>{f.icon}</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{f.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Banner */}
      <section className="bg-blue-600 py-14">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[['1.000+', 'Loại thuốc'], ['500+', 'Bệnh lý'], ['10.000+', 'Lượt tra cứu'], ['98%', 'Độ chính xác AI']].map(([n, l]) => (
              <div key={l}>
                <p className="text-4xl font-bold text-white mb-1">{n}</p>
                <p className="text-blue-200 font-medium">{l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;