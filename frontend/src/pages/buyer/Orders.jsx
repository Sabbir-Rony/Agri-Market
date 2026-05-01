import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersAPI, paymentsAPI } from '../../services/api';
import { Clock, Check, Truck, DollarSign } from 'lucide-react';

export default function BuyerOrders() {
  const queryClient = useQueryClient();
  const [showPaymentModal, setShowPaymentModal] = useState(null);
  const [paymentData, setPaymentData] = useState({ method: 'bkash', transaction_id: '' });

  const { data: orders, isLoading } = useQuery({
    queryKey: ['buyer-orders'],
    queryFn: () => ordersAPI.list().then(res => res.data)
  });

  const payAdvanceMutation = useMutation({
    mutationFn: (data) => paymentsAPI.advance(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['buyer-orders']);
      setShowPaymentModal(null);
    }
  });

  const payFinalMutation = useMutation({
    mutationFn: (data) => paymentsAPI.final(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['buyer-orders']);
      setShowPaymentModal(null);
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

  const handlePayAdvance = (order) => {
    payAdvanceMutation.mutate({
      order_id: order.id,
      payment_type: 'advance',
      method: paymentData.method,
      amount: order.advance_amount,
      transaction_id: paymentData.transaction_id
    });
  };

  const handlePayFinal = (order) => {
    payFinalMutation.mutate({
      order_id: order.id,
      payment_type: 'final',
      method: paymentData.method,
      amount: order.due_amount,
      transaction_id: paymentData.transaction_id
    });
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Orders</h1>
        <p className="text-gray-600">Track your orders and make payments</p>
      </div>

      {orders?.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl">
          <p className="text-gray-600 mb-4">You haven't placed any orders yet</p>
          <a href="/products" className="btn-primary">Browse Products</a>
        </div>
      ) : (
        <div className="space-y-4">
          {orders?.map(order => (
            <div key={order.id} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-lg">{order.product_title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(order.status)}`}>
                      {order.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">Order: {order.order_number}</p>
                  <p className="text-sm text-gray-600">Farmer: {order.farmer_name}</p>
                  <p className="text-sm text-gray-600">Quantity: {order.ordered_qty} kg</p>
                  
                  <div className="mt-3 space-y-1">
                    <p className="font-medium">Total: ৳{order.total_amount}</p>
                    <p className="text-sm text-gray-600">Advance (30%): ৳{order.advance_amount}</p>
                    <p className="text-sm text-gray-600">Due (70%): ৳{order.due_amount}</p>
                  </div>
                  
                  {order.expected_delivery_date && (
                    <p className="text-sm text-gray-500 mt-2">
                      Expected Delivery: {new Date(order.expected_delivery_date).toLocaleDateString()}
                    </p>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="space-y-2">
                  {order.status === 'advance_pending' && (
                    <button
                      onClick={() => setShowPaymentModal({ type: 'advance', order })}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <DollarSign className="w-4 h-4" />
                      Pay 30% Advance
                    </button>
                  )}
                  
                  {order.status === 'delivered_pending_final_payment' && (
                    <button
                      onClick={() => setShowPaymentModal({ type: 'final', order })}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <DollarSign className="w-4 h-4" />
                      Pay 70% Due
                    </button>
                  )}
                  
                  {order.status === 'awaiting_farmers_approval' && (
                    <div className="flex items-center gap-2 text-yellow-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">Waiting for farmer approval</span>
                    </div>
                  )}
                  
                  {order.status === 'approved' && (
                    <div className="flex items-center gap-2 text-green-600">
                      <Check className="w-4 h-4" />
                      <span className="text-sm">Order confirmed</span>
                    </div>
                  )}
                  
                  {(order.status === 'scheduled' || order.status === 'out_for_delivery') && (
                    <div className="flex items-center gap-2 text-blue-600">
                      <Truck className="w-4 h-4" />
                      <span className="text-sm">In transit</span>
                    </div>
                  )}
                  
                  {order.status === 'completed' && (
                    <div className="flex items-center gap-2 text-green-600">
                      <Check className="w-4 h-4" />
                      <span className="text-sm">Order completed</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {showPaymentModal.type === 'advance' ? 'Pay Advance (30%)' : 'Pay Final (70%)'}
            </h3>
            <p className="text-gray-600 mb-4">
              Amount: ৳{showPaymentModal.type === 'advance' 
                ? showPaymentModal.order.advance_amount 
                : showPaymentModal.order.due_amount}
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="label">Payment Method</label>
                <select
                  value={paymentData.method}
                  onChange={(e) => setPaymentData({ ...paymentData, method: e.target.value })}
                  className="input"
                >
                  <option value="bkash">bKash</option>
                  <option value="nagad">Nagad</option>
                  <option value="cash">Cash</option>
                  <option value="bank">Bank Transfer</option>
                </select>
              </div>
              <div>
                <label className="label">Transaction ID (optional)</label>
                <input
                  type="text"
                  value={paymentData.transaction_id}
                  onChange={(e) => setPaymentData({ ...paymentData, transaction_id: e.target.value })}
                  className="input"
                  placeholder="Enter transaction ID"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  if (showPaymentModal.type === 'advance') {
                    handlePayAdvance(showPaymentModal.order);
                  } else {
                    handlePayFinal(showPaymentModal.order);
                  }
                }}
                disabled={payAdvanceMutation.isPending || payFinalMutation.isPending}
                className="flex-1 btn-primary"
              >
                Confirm Payment
              </button>
              <button
                onClick={() => setShowPaymentModal(null)}
                className="px-4 py-2 border rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}