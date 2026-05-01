import { useQuery } from '@tanstack/react-query';
import { dashboardAPI } from '../../services/api';
import { Package, ShoppingCart, DollarSign, Truck, XCircle, Shield } from 'lucide-react';

export default function FarmerDashboard() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['farmer-dashboard'],
    queryFn: () => dashboardAPI.farmer().then(res => res.data)
  });

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  const stats = [
    { label: 'Total Products', value: dashboard?.total_products || 0, icon: Package, color: 'bg-blue-500' },
    { label: 'Advance Orders', value: dashboard?.total_advance_orders || 0, icon: ShoppingCart, color: 'bg-purple-500' },
    { label: 'Confirmed Orders', value: dashboard?.total_confirmed_orders || 0, icon: ShoppingCart, color: 'bg-green-500' },
    { label: 'Advance Received', value: `৳${(dashboard?.total_advance_received || 0).toFixed(0)}`, icon: DollarSign, color: 'bg-yellow-500' },
    { label: 'Pending Deliveries', value: dashboard?.pending_deliveries || 0, icon: Truck, color: 'bg-orange-500' },
    { label: 'Cancelled Orders', value: dashboard?.cancelled_orders || 0, icon: XCircle, color: 'bg-red-500' },
    { label: 'Pending Claims', value: dashboard?.pending_claims || 0, icon: Shield, color: 'bg-indigo-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Farmer Dashboard</h1>
        <p className="text-gray-600">Overview of your farm business</p>
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
      <div className="grid md:grid-cols-3 gap-6">
        <a href="/farmer/products/add" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Package className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Add New Product</h3>
          <p className="text-gray-600 text-sm">List your pre-harvest crops</p>
        </a>
        <a href="/farmer/orders" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <ShoppingCart className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">View Orders</h3>
          <p className="text-gray-600 text-sm">Manage incoming orders</p>
        </a>
        <a href="/farmer/claims" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Shield className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Insurance Claims</h3>
          <p className="text-gray-600 text-sm">Submit crop loss claims</p>
        </a>
      </div>
    </div>
  );
}