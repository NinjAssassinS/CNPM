import { useEffect, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import DiseaseCard from '@/components/DiseaseCard';
import client from '@/lib/client';

const SearchPage = () => {
  const [diseases, setDiseases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('');
  const [showFilters, setShowFilters] = useState(false);

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

  const groups = [...new Set(diseases.map((d) => d.group_name).filter(Boolean))];
  const riskLevels = [...new Set(diseases.map((d) => d.risk_level).filter(Boolean))];

  const filteredDiseases = diseases.filter((disease) => {
    const matchesSearch =
      !searchQuery ||
      disease.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      disease.symptoms?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      disease.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGroup = !selectedGroup || disease.group_name === selectedGroup;
    const matchesRisk = !selectedRisk || disease.risk_level === selectedRisk;
    return matchesSearch && matchesGroup && matchesRisk;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">Tra cứu bệnh lý</h1>
          <p className="text-slate-500 text-sm mt-1">Tìm kiếm thông tin bệnh lý và triệu chứng</p>
        </div>

        <div className="flex gap-3 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm theo tên bệnh hoặc triệu chứng..."
              className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="md:hidden px-4 bg-white border border-slate-200 rounded-xl text-slate-700 hover:bg-slate-50"
          >
            <Filter className="h-5 w-5" />
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          <aside className={`${showFilters ? 'block' : 'hidden'} lg:block w-full lg:w-64 flex-shrink-0`}>
            <div className="bg-white rounded-2xl border border-slate-200 p-5 sticky top-24">
              <div className="flex items-center gap-2 mb-5">
                <Filter className="h-4 w-4 text-blue-600" />
                <h3 className="font-semibold text-slate-900">Bộ lọc</h3>
              </div>

              <div className="mb-6">
                <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-3">Nhóm bệnh</h4>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="group" checked={selectedGroup === ''} onChange={() => setSelectedGroup('')} className="text-blue-600" />
                    <span className="text-sm text-slate-600">Tất cả</span>
                  </label>
                  {groups.map((group) => (
                    <label key={group} className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="group" checked={selectedGroup === group} onChange={() => setSelectedGroup(group)} className="text-blue-600" />
                      <span className="text-sm text-slate-600">{group}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-3">Mức độ nguy cơ</h4>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="risk" checked={selectedRisk === ''} onChange={() => setSelectedRisk('')} className="text-blue-600" />
                    <span className="text-sm text-slate-600">Tất cả</span>
                  </label>
                  {riskLevels.map((level) => (
                    <label key={level} className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="risk" checked={selectedRisk === level} onChange={() => setSelectedRisk(level)} className="text-blue-600" />
                      <span className="text-sm text-slate-600">{level}</span>
                    </label>
                  ))}
                </div>
              </div>

              {(selectedGroup || selectedRisk) && (
                <button
                  onClick={() => { setSelectedGroup(''); setSelectedRisk(''); }}
                  className="w-full h-9 border border-slate-200 rounded-lg text-sm text-slate-500 hover:bg-slate-50 transition-colors"
                >
                  Xóa bộ lọc
                </button>
              )}
            </div>
          </aside>

          <main className="flex-1">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
              </div>
            ) : filteredDiseases.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
                <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">Không tìm thấy kết quả</h3>
                <p className="text-sm text-slate-500">Thử thay đổi từ khóa hoặc bộ lọc</p>
              </div>
            ) : (
              <>
                <p className="text-sm text-slate-500 mb-4">
                  Tìm thấy <span className="font-semibold text-slate-900">{filteredDiseases.length}</span> kết quả
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {filteredDiseases.map((disease) => (
                    <DiseaseCard key={disease.id} disease={disease} />
                  ))}
                </div>
              </>
            )}
          </main>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default SearchPage;