import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Pill, Users, Brain, ChevronLeft, AlertTriangle, CheckCircle, TrendingUp, ExternalLink } from 'lucide-react';
import client, { api } from '@/lib/client';

const AdminDashboard = () => {
  const [diseases, setDiseases] = useState<any[]>([]);
  const [drugs, setDrugs] = useState<any[]>([]);
  const [mappings, setMappings] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [diseasesRes, mappingsRes] = await Promise.all([
          client.entities.diseases.query({ limit: 100 }),
          client.entities.disease_drug_mappings.query({ limit: 100 }),
        ]);
        setDiseases(diseasesRes.data?.items || []);
        setMappings(mappingsRes.data?.items || []);
      } catch (err) {
        console.error('Failed to fetch admin data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const tabs = [
    { id: 'overview', label: 'Tổng quan' },
    { id: 'drugs', label: 'Quản lý thuốc' },
    { id: 'diseases', label: 'Quản lý bệnh' },
    { id: 'mappings', label: 'Mapping Bệnh-Thuốc' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Admin Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-lg text-slate-900">Medi<span className="text-blue-600">Admin</span></span>
            </div>
            <Link to="/" className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 transition-colors">
              <ChevronLeft className="h-4 w-4" /> Về trang chủ
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-white border border-slate-200 rounded-xl p-1.5 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 h-9 rounded-lg text-sm font-medium transition-colors whitespace-nowrap px-4 ${
                activeTab === tab.id ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview */}
        {activeTab === 'overview' && (
          <div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {[
                { icon: <Pill className="h-6 w-6 text-blue-600" />, label: 'Tổng số thuốc (OpenFDA)', value: 'API', color: 'bg-blue-50' },
                { icon: <Activity className="h-6 w-6 text-emerald-600" />, label: 'Tổng số bệnh', value: String(diseases.length), color: 'bg-emerald-50' },
                { icon: <Users className="h-6 w-6 text-amber-600" />, label: 'Mapping', value: String(mappings.length), color: 'bg-amber-50' },
                { icon: <Brain className="h-6 w-6 text-purple-600" />, label: 'Nhóm bệnh', value: String(new Set(diseases.map(d => d.group_name)).size), color: 'bg-purple-50' },
              ].map((stat) => (
                <div key={stat.label} className="bg-white rounded-2xl p-6 border border-slate-200">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-slate-500 font-medium">{stat.label}</p>
                      <p className="text-3xl font-bold text-slate-900 mt-1">{stat.value}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${stat.color}`}>
                      {stat.icon}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Alerts */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <h3 className="font-semibold text-slate-900 mb-4">Thông tin hệ thống</h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-emerald-50 rounded-xl">
                  <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5" />
                  <p className="text-xs text-slate-700">Hệ thống hoạt động bình thường</p>
                </div>
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
                  <TrendingUp className="h-4 w-4 text-blue-500 mt-0.5" />
                  <p className="text-xs text-slate-700">{drugs.length} thuốc và {diseases.length} bệnh lý trong cơ sở dữ liệu</p>
                </div>
                <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-xl">
                  <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5" />
                  <p className="text-xs text-slate-700">AI model sử dụng: deepseek-v4-pro</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Drugs Management */}
        {activeTab === 'drugs' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-2">Quản lý thuốc (OpenFDA)</h3>
            <p className="text-sm text-slate-500 mb-4">
              Dữ liệu thuốc được lấy trực tiếp từ <a href="https://open.fda.gov" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenFDA</a>.
              Không có dữ liệu thuốc cục bộ.
            </p>
            <Link
              to="/drugs"
              className="inline-flex items-center gap-2 text-sm text-blue-600 hover:underline"
            >
              <ExternalLink className="h-4 w-4" /> Tra cứu thuốc
            </Link>
          </div>
        )}

        {/* Diseases Management */}
        {activeTab === 'diseases' && (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Danh sách bệnh lý ({diseases.length})</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    {['Icon', 'Tên bệnh', 'Nhóm', 'Mức độ', 'Mô tả'].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {diseases.map((disease) => (
                    <tr key={disease.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-4 py-3 text-2xl">{disease.icon || '🏥'}</td>
                      <td className="px-4 py-3">
                        <p className="text-sm font-medium text-slate-900">{disease.name}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{disease.group_name}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          disease.risk_level === 'high' ? 'bg-red-50 text-red-600' : disease.risk_level === 'medium' ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                        }`}>{disease.risk_level === 'high' ? 'Cao' : disease.risk_level === 'medium' ? 'Trung bình' : 'Thấp'}</span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600 max-w-xs truncate">{disease.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Mappings */}
        {activeTab === 'mappings' && (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200">
              <h3 className="font-semibold text-slate-900">Mapping Bệnh - Thuốc ({mappings.length})</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    {['Bệnh', 'Thuốc', 'Ưu tiên', 'Điểm phù hợp'].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {mappings.map((mapping) => {
                    const disease = diseases.find(d => d.id === mapping.disease_id);
                    return (
                      <tr key={mapping.id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm text-slate-900">{disease?.name || `ID: ${mapping.disease_id}`}</td>
                        <td className="px-4 py-3 text-sm text-slate-900">
                          <Link to={`/drug/${encodeURIComponent(mapping.drug_name)}`} className="text-blue-600 hover:underline inline-flex items-center gap-1">
                            {mapping.drug_name} <ExternalLink className="h-3 w-3" />
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">#{mapping.priority}</td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
                            {mapping.match_score}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;