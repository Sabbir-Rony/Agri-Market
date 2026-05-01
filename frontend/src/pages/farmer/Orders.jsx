import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersAPI, paymentsAPI } from '../../services/api';
import { Check, X, Clock, Truck } from 'lucide-react';

export default function FarmerOrders() {
  const queryClient = useQueryClient();

  const { data: orders, isLoading } = useQuery({
    queryKey: ['farmer-orders'],
    queryFn: () => ordersAPI.list({ role: 'farmer' }).then(res => res.data)
  });

  const { data: incomingOrders } = useQuery({
    queryKey: ['incoming-orders'],
    queryFn: () => ordersAPI.incoming().then(res => res.data)
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, data }) => ordersAPI.approve(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['farmer-orders']);
      queryClient.invalidateQueries(['incoming-orders']);
    }
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, data }) => ordersAPI.reject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['farmer-orders']);
      queryClient.invalidateQueries(['incoming-orders']);
    }
  });

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-700',
      'advance_pending': 'bg-yellow-100 text-yellow-700',
      'advance_paid': 'bg-blue-100 text-blue-700',
      'awaiting_farmers_approval': 'bg-purple-100 text-purple-700',
      'approved': 'bg-green-100 text-green-700',
      'rejected': 'bg-red-100 text-red-700',
      'scheduled': 'bg-indigo-100 text-indigo-700',
      'out_for_delivery': 'bg-orange-100 text-orange-700',
      'delivered_pending_final_payment': 'bg-teal-100 text-teal-700',
      'completed': 'bg-green-100 text-green-700',
      'cancelled': 'bg-red-100 text-red-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Incoming Orders (Pending Approval) */}
      {incomingOrders && incomingOrders.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-yellow-600" />
            Pending Approval ({incomingOrders.length})
          </h2>
          <div className="space-y-4">
            {incomingOrders.map(order => (
              <div key={order.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{order.product_title}</p>
                    <p className="text-sm text-gray-600">
                      Order: {order.order_number} | Qty: {order.ordered_qty} kg
                    </p>
                    <p className="text-sm text-gray-600">Buyer: {order.buyer_name}</p>
                    <p className="mt-2">
                      <span className="font-medium">Total: ৳{order.total_amount}</span>
                      <span className="text-gray-500"> (Advance: ৳{order.advance_amount})</span>
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => approveMutation.mutate({ id: order.id, data: {} })}
                      disabled={approveMutation.isPending}
                      className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => {
                        const reason = prompt('Enter rejection reason:');
                        if (reason) rejectMutation.mutate({ id: order.id, data: { reason } });
                      }}
                      disabled={rejectMutation.isPending}
                      className="flex items-center gap-1 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Orders */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">All Orders</h2>
        {orders?.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No orders yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Order</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Product</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Buyer</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Amount</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {orders?.map(order => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <p className="font-medium">{order.order_number}</p>
                      <p className="text-sm text-gray-500">{order.ordered_qty} kg</p>
                    </td>
                    <td className="px-4 py-3">{order.product_title}</td>
                    <td className="px-4 py-3">{order.buyer_name}</td>
                    <td className="px-4 py-3">
                      <p className="font-medium">৳{order.total_amount}</p>
                      <p className="text-sm text-gray-500">Advance: ৳{order.advance_amount}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(order.status)}`}>
                        {order.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}