import { useQuery } from '@tanstack/react-query';
import { dashboardAPI } from '../../services/api';
import { Users, Package, ShoppingCart, Shield, DollarSign, UserCheck, AlertTriangle } from 'lucide-react';

export default function AdminDashboard() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => dashboardAPI.admin().then(res => res.data)
  });

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  const stats = [
    { label: 'Total Farmers', value: dashboard?.total_farmers || 0, icon: Users, color: 'bg-blue-500' },
    { label: 'Total Buyers', value: dashboard?.total_buyers || 0, icon: Users, color: 'bg-purple-500' },
    { label: 'Total Products', value: dashboard?.total_products || 0, icon: Package, color: 'bg-green-500' },
    { label: 'Total Orders', value: dashboard?.total_orders || 0, icon: ShoppingCart, color: 'bg-yellow-500' },
    { label: 'Pending Verifications', value: dashboard?.pending_farmer_verifications || 0, icon: UserCheck, color: 'bg-orange-500' },
    { label: 'Pending Claims', value: dashboard?.pending_claims || 0, icon: Shield, color: 'bg-red-500' },
    { label: 'Total Revenue', value: `৳${(dashboard?.total_revenue || 0).toFixed(0)}`, icon: DollarSign, color: 'bg-indigo-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Platform overview and management</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-sm p-6">
            <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-sm text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-4 gap-6">
        <a href="/admin/users" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Users className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">User Management</h3>
          <p className="text-gray-600 text-sm">Manage farmers and buyers</p>
        </a>
        <a href="/admin/products" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Package className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Product Moderation</h3>
          <p className="text-gray-600 text-sm">Review and approve products</p>
        </a>
        <a href="/admin/claims" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Shield className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Insurance Claims</h3>
          <p className="text-gray-600 text-sm">Review crop loss claims</p>
        </a>
        <a href="/admin/disputes" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <AlertTriangle className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Disputes</h3>
          <p className="text-gray-600 text-sm">Handle order disputes</p>
        </a>
      </div>
    </div>
  );
}