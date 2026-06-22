import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Star, Bookmark, RefreshCw, AlertTriangle, Activity, Shield, ExternalLink } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import client from '@/lib/client';
import { api } from '@/lib/client';

const DrugDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [drug, setDrug] = useState<any>(null);
  const [fdaData, setFdaData] = useState<any>(null);
  const [fdaLoading, setFdaLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    const fetchDrug = async () => {
      try {
        const response = await client.entities.drugs.get({ id: id! });
        setDrug(response.data);
        fetchFDAData(response.data);
      } catch (err) {
        console.error('Failed to fetch drug:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrug();
  }, [id]);

  const fetchFDAData = async (drugData?: any) => {
    const target = drugData || drug;
    if (!target) return;
    setFdaLoading(true);
    try {
      const res = await api.get('/api/v1/openfda/enrich', {
        params: {
          brand_name: target.name || '',
          generic_name: target.component || '',
        },
        timeout: 15000,
      });
      setFdaData(res.data);
    } catch {
      console.warn('FDA data fetch failed (non-critical)');
    } finally {
      setFdaLoading(false);
    }
  };

  const checkSavedStatus = async () => {
    try {
      const res = await api.get('/api/v1/user/saved-drugs');
      const savedItems = res.data?.items || [];
      setIsSaved(savedItems.some((item: any) => item.drug_id === Number(id)));
    } catch {
      // not logged in or error
    }
  };

  const toggleSaveDrug = async () => {
    try {
      if (isSaved) {
        await api.delete(`/api/v1/user/saved-drugs/${id}`);
        setIsSaved(false);
      } else {
        await api.post(`/api/v1/user/saved-drugs/${id}`);
        setIsSaved(true);
      }
    } catch {
      console.error('Failed to toggle save drug');
    }
  };

  useEffect(() => {
    checkSavedStatus();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
        </div>
      </div>
    );
  }

  if (!drug) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <div className="text-center py-20">
          <p className="text-slate-500">Không tìm thấy thuốc</p>
        </div>
      </div>
    );
  }

  const hasFDA = fdaData && (fdaData.label || fdaData.adverse_events || fdaData.recalls);

  const tabs = [
    { id: 'overview', label: 'Tổng quan' },
    { id: 'usage', label: 'Công dụng' },
    { id: 'dosage', label: 'Liều dùng' },
    { id: 'side_effects', label: 'Tác dụng phụ' },
    { id: 'contraindications', label: 'Chống chỉ định' },
    ...(hasFDA ? [{ id: 'fda_label', label: 'FDA Nhãn thuốc' }] : []),
    ...(hasFDA && fdaData?.adverse_events ? [{ id: 'fda_events', label: 'FDA Tác dụng phụ' }] : []),
    ...(hasFDA && fdaData?.recalls ? [{ id: 'fda_recalls', label: 'FDA Thu hồi' }] : []),
  ];

  const rating = drug.rating || 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-6 transition-colors">
          <ChevronLeft className="h-4 w-4" /> Quay lại
        </button>

        {/* Drug Header */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 mb-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="w-32 h-32 bg-blue-50 rounded-2xl flex items-center justify-center text-6xl flex-shrink-0">💊</div>
            <div className="flex-1">
              <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold text-slate-900">{drug.name}</h1>
                    {drug.data_source === 'local' && (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">CSDL</span>
                    )}
                    {drug.data_source === 'openfda' && (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700">openFDA</span>
                    )}
                  </div>
                  <p className="text-slate-500 mt-1">{drug.manufacturer} · Mã: {drug.code}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={toggleSaveDrug}
                    className={`h-10 px-5 font-medium rounded-xl transition-colors flex items-center gap-2 ${
                      isSaved
                        ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    <Bookmark className={`h-4 w-4 ${isSaved ? 'fill-blue-700' : ''}`} />
                    {isSaved ? 'Đã lưu' : 'Lưu thuốc'}
                  </button>
                  <button
                    onClick={() => fetchFDAData(drug)}
                    disabled={fdaLoading}
                    className="h-10 w-10 border border-slate-200 rounded-xl flex items-center justify-center text-slate-400 hover:text-blue-600 hover:border-blue-300 transition-colors"
                    title="Tải lại dữ liệu FDA"
                  >
                    <RefreshCw className={`h-4 w-4 ${fdaLoading ? 'animate-spin' : ''}`} />
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-3 mb-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{drug.group_name}</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${drug.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                  {drug.status === 'active' ? 'Đang lưu hành' : 'Ngừng lưu hành'}
                </span>
                <span className="text-sm font-semibold text-blue-600">{drug.price} / hộp</span>
              </div>
              <div className="flex items-center gap-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className={`h-5 w-5 ${i < Math.floor(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-200 fill-slate-200'}`} />
                ))}
                <span className="font-semibold text-slate-900">{rating.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-200 px-2 overflow-x-auto">
            <div className="flex gap-1 py-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          <div className="p-6 md:p-8">
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="font-semibold text-slate-900 mb-4">Thông tin chung</h3>
                  <dl className="space-y-3">
                    {[
                      ['Tên hoạt chất', drug.component || 'N/A'],
                      ['Nhóm thuốc', drug.group_name],
                      ['Nhà sản xuất', drug.manufacturer],
                      ['Mã thuốc', drug.code],
                      ['Trạng thái', drug.status === 'active' ? 'Đang lưu hành' : 'Ngừng lưu hành'],
                      ['Giá', drug.price || 'N/A'],
                    ].map(([k, v]) => (
                      <div key={k} className="flex justify-between py-2 border-b border-slate-100 last:border-0">
                        <dt className="text-sm text-slate-500">{k}</dt>
                        <dd className="text-sm font-medium text-slate-900">{v}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-4">Bảo quản</h3>
                  <div className="bg-blue-50 rounded-xl p-4 space-y-3">
                    {[['🌡️', 'Nhiệt độ', 'Dưới 30°C'], ['💧', 'Độ ẩm', 'Nơi khô ráo'], ['☀️', 'Ánh sáng', 'Tránh ánh nắng'], ['📅', 'Hạn dùng', '36 tháng']].map(([emoji, k, v]) => (
                      <div key={k} className="flex items-center gap-3">
                        <span className="text-xl">{emoji}</span>
                        <span className="text-sm text-slate-500 flex-1">{k}</span>
                        <span className="text-sm font-medium text-slate-900">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'usage' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Công dụng</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.usage_info || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'dosage' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Liều dùng</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.dosage || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'side_effects' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Tác dụng phụ</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.side_effects || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'contraindications' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Chống chỉ định</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.contraindications || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'fda_label' && fdaData?.label && (
              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-4">
                  <Shield className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">Thông tin nhãn thuốc từ FDA</h3>
                  <a href="https://www.fda.gov/drugs" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1 ml-auto">
                    Nguồn: FDA <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                {fdaData.label.indications_and_usage?.length > 0 && (
                  <div className="bg-blue-50 rounded-xl p-4">
                    <h4 className="font-semibold text-slate-900 text-sm mb-2">Chỉ định & Công dụng</h4>
                    {fdaData.label.indications_and_usage.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-slate-600 mb-1">{text}</p>
                    ))}
                  </div>
                )}
                {fdaData.label.boxed_warning?.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="h-5 w-5 text-red-500" />
                      <h4 className="font-semibold text-red-800 text-sm">Cảnh báo đóng hộp (Boxed Warning)</h4>
                    </div>
                    {fdaData.label.boxed_warning.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-red-700 mb-1">{text}</p>
                    ))}
                  </div>
                )}
                {fdaData.label.warnings?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm mb-2">Cảnh báo</h4>
                    {fdaData.label.warnings.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-slate-600 mb-1">{text}</p>
                    ))}
                  </div>
                )}
                {fdaData.label.dosage_and_administration?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm mb-2">Liều dùng & Cách dùng</h4>
                    {fdaData.label.dosage_and_administration.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-slate-600 mb-1">{text}</p>
                    ))}
                  </div>
                )}
                {fdaData.label.drug_interactions?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm mb-2">Tương tác thuốc</h4>
                    {fdaData.label.drug_interactions.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-slate-600 mb-1">{text}</p>
                    ))}
                  </div>
                )}
                {fdaData.label.purpose?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm mb-2">Mục đích sử dụng</h4>
                    {fdaData.label.purpose.map((text: string, i: number) => (
                      <p key={i} className="text-sm text-slate-600 mb-1">{text}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
            {activeTab === 'fda_events' && fdaData?.adverse_events && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="h-5 w-5 text-amber-600" />
                  <h3 className="font-semibold text-slate-900">Phản ứng có hại (Adverse Events) từ FDA</h3>
                  <a href="https://www.fda.gov/drugs" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1 ml-auto">
                    Nguồn: FAERS <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div className="space-y-3">
                  {fdaData.adverse_events.map((event: any, i: number) => (
                    <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 hover:border-amber-200 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        {event.serious && <span className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-full font-medium">Nghiêm trọng</span>}
                        {event.seriousnesshospitalization && <span className="px-2 py-0.5 bg-amber-50 text-amber-700 text-xs rounded-full font-medium">Nhập viện</span>}
                        {event.seriousnessdeath && <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-medium">Tử vong</span>}
                      </div>
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {event.reactions?.map((r: string, j: number) => (
                          <span key={j} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-full">{r}</span>
                        ))}
                      </div>
                      {event.receivedate && (
                        <p className="text-xs text-slate-400">Ngày báo cáo: {event.receivedate}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeTab === 'fda_recalls' && fdaData?.recalls && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <h3 className="font-semibold text-slate-900">Thông tin thu hồi từ FDA</h3>
                  <a href="https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1 ml-auto">
                    Nguồn: FDA <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div className="space-y-3">
                  {fdaData.recalls.map((recall: any, i: number) => (
                    <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 hover:border-red-200 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                          recall.classification === 'Class I' ? 'bg-red-50 text-red-600' :
                          recall.classification === 'Class II' ? 'bg-amber-50 text-amber-700' :
                          'bg-slate-100 text-slate-600'
                        }`}>{recall.classification || 'N/A'}</span>
                        <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full font-medium">{recall.recall_status}</span>
                      </div>
                      {recall.product_description && (
                        <p className="text-sm font-medium text-slate-900 mb-1">{recall.product_description}</p>
                      )}
                      {recall.recall_reason && (
                        <p className="text-sm text-slate-600 mb-1"><span className="font-medium">Lý do:</span> {recall.recall_reason}</p>
                      )}
                      {recall.recalling_firm && (
                        <p className="text-xs text-slate-500">Công ty: {recall.recalling_firm}</p>
                      )}
                      {recall.report_date && (
                        <p className="text-xs text-slate-400">Ngày báo cáo: {recall.report_date}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DrugDetailPage;