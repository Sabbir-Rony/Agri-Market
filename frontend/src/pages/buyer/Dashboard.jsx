import { useQuery } from '@tanstack/react-query';
import { dashboardAPI } from '../../services/api';
import { Package, ShoppingCart, DollarSign, Truck, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function BuyerDashboard() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['buyer-dashboard'],
    queryFn: () => dashboardAPI.buyer().then(res => res.data)
  });

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  const stats = [
    { label: 'Total Orders', value: dashboard?.total_orders || 0, icon: ShoppingCart, color: 'bg-blue-500' },
    { label: 'Advance Paid', value: `৳${(dashboard?.total_advance_paid || 0).toFixed(0)}`, icon: DollarSign, color: 'bg-green-500' },
    { label: 'Due Remaining', value: `৳${(dashboard?.total_due_remaining || 0).toFixed(0)}`, icon: DollarSign, color: 'bg-yellow-500' },
    { label: 'Pending Delivery', value: dashboard?.pending_deliveries || 0, icon: Truck, color: 'bg-orange-500' },
    { label: 'Completed', value: dashboard?.completed_orders || 0, icon: CheckCircle, color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Buyer Dashboard</h1>
        <p className="text-gray-600">Your orders and payments overview</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
      <div className="grid md:grid-cols-2 gap-6">
        <Link to="/products" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <Package className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">Browse Products</h3>
          <p className="text-gray-600 text-sm">Find pre-harvest crops</p>
        </Link>
        <Link to="/buyer/orders" className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <ShoppingCart className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-lg">My Orders</h3>
          <p className="text-gray-600 text-sm">Track your orders and payments</p>
        </Link>
      </div>
    </div>
  );
}