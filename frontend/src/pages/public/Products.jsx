import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productsAPI } from '../../services/api';
import { Search, Filter, MapPin, Calendar, Shield } from 'lucide-react';

export default function Products() {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    crop_type: '',
    district: '',
    insurance_enabled: false
  });
  const [showFilters, setShowFilters] = useState(false);

  const { data: products, isLoading } = useQuery({
    queryKey: ['products', filters],
    queryFn: () => {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.category) params.category = filters.category;
      if (filters.crop_type) params.crop_type = filters.crop_type;
      if (filters.district) params.district = filters.district;
      if (filters.insurance_enabled) params.insurance_enabled = true;
      return productsAPI.list(params).then(res => res.data);
    }
  });

  const categories = ['vegetables', 'fruits', 'grains', 'spices', 'others'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Browse Products</h1>
          <p className="text-gray-600">Find pre-harvest crops from verified farmers</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <Filter className="w-5 h-5" />
          Filters
        </button>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search crops, farmers..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="input pl-10"
          />
        </div>

        {showFilters && (
          <div className="grid md:grid-cols-4 gap-4 p-4 bg-white rounded-lg border">
            <div>
              <label className="label">Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                className="input"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Crop Type</label>
              <input
                type="text"
                placeholder="e.g., Rice, Potato"
                value={filters.crop_type}
                onChange={(e) => setFilters({ ...filters, crop_type: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">District</label>
              <input
                type="text"
                placeholder="e.g., Dhaka"
                value={filters.district}
                onChange={(e) => setFilters({ ...filters, district: e.target.value })}
                className="input"
              />
            </div>
            <div className="flex items-center">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.insurance_enabled}
                  onChange={(e) => setFilters({ ...filters, insurance_enabled: e.target.checked })}
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <span className="text-sm text-gray-700">Insurance Available</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Products Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading products...</p>
        </div>
      ) : products?.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">No products found. Try different filters.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products?.map(product => (
            <Link
              key={product.id}
              to={`/products/${product.id}`}
              className="bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow"
            >
              {/* Product Image */}
              <div className="h-48 bg-gray-100 rounded-t-xl overflow-hidden">
                {product.primary_image ? (
                  <img
                    src={product.primary_image}
                    alt={product.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    No Image
                  </div>
                )}
              </div>

              {/* Product Info */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg text-gray-900">{product.title}</h3>
                  {product.insurance_enabled && (
                    <Shield className="w-5 h-5 text-primary-600" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-3">{product.crop_type}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    {product.district || 'Location not specified'}
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="w-4 h-4" />
                    {product.expected_harvest_date 
                      ? new Date(product.expected_harvest_date).toLocaleDateString()
                      : 'Harvest date not set'}
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between">
                  <div>
                    <span className="text-2xl font-bold text-primary-600">৳{product.price_per_kg}</span>
                    <span className="text-sm text-gray-500">/{product.unit}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Min: {product.min_order_qty} {product.unit}
                  </div>
                </div>

                <div className="mt-3 text-sm text-gray-500">
                  Available: {product.available_qty} {product.unit}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}