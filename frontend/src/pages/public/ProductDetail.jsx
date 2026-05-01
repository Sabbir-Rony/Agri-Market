import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productsAPI, ordersAPI, resolveImageUrl } from '../../services/api';
import { useAuthStore } from '../../context/AuthContext';
import { MapPin, Calendar, Shield, Package, User, ArrowLeft } from 'lucide-react';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, user } = useAuthStore();
  const [orderQty, setOrderQty] = useState('');
  const [showOrderForm, setShowOrderForm] = useState(false);

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productsAPI.get(id).then(res => res.data)
  });

  const createOrderMutation = useMutation({
    mutationFn: (data) => ordersAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      navigate('/buyer/orders');
    }
  });

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Product not found</p>
        <Link to="/products" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to products
        </Link>
      </div>
    );
  }

  const handleOrder = (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (user?.role !== 'buyer') {
      alert('Only buyers can place orders');
      return;
    }
    createOrderMutation.mutate({
      product_id: product.id,
      ordered_qty: parseFloat(orderQty)
    });
  };

  const totalAmount = orderQty ? parseFloat(orderQty) * product.price_per_kg : 0;
  const advanceAmount = totalAmount * 0.3;
  const dueAmount = totalAmount * 0.7;

  return (
    <div className="space-y-6">
      <Link to="/products" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" />
        Back to Products
      </Link>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Product Images */}
        <div className="space-y-4">
          <div className="bg-gray-100 rounded-xl h-80 overflow-hidden">
            {product.images?.[0]?.image_url ? (
              <img
                src={resolveImageUrl(product.images[0].image_url)}
                alt={product.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No Image Available
              </div>
            )}
          </div>
          {product.images?.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.slice(1).map((img, idx) => (
                <div key={idx} className="bg-gray-100 rounded-lg h-20 overflow-hidden">
                  <img src={resolveImageUrl(img.image_url)} alt="" className="w-full h-full object-cover" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Product Details */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                {product.category}
              </span>
              {product.insurance_enabled && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1">
                  <Shield className="w-4 h-4" />
                  Insured
                </span>
              )}
            </div>
            <h1 className="text-3xl font-bold text-gray-900">{product.title}</h1>
            <p className="text-lg text-gray-600 mt-1">{product.crop_type}</p>
          </div>

          <div className="flex items-center gap-4">
            <div>
              <span className="text-3xl font-bold text-primary-600">৳{product.price_per_kg}</span>
              <span className="text-gray-500">/{product.unit}</span>
            </div>
            <div className="text-sm text-gray-500">
              Min order: {product.min_order_qty} {product.unit}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">Available</p>
              <p className="font-semibold">{product.available_qty} {product.unit}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">Expected Harvest</p>
              <p className="font-semibold">
                {product.expected_harvest_date 
                  ? new Date(product.expected_harvest_date).toLocaleDateString()
                  : 'Not set'}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-gray-600">
              <User className="w-5 h-5" />
              <span>Farmer: {product.farmer_name}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <MapPin className="w-5 h-5" />
              <span>
                {product.upazila}, {product.district}
              </span>
            </div>
            {product.expected_delivery_date && (
              <div className="flex items-center gap-2 text-gray-600">
                <Calendar className="w-5 h-5" />
                <span>
                  Delivery: {new Date(product.expected_delivery_date).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>

          {product.description && (
            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-gray-600">{product.description}</p>
            </div>
          )}

          {/* Order Form */}
          {showOrderForm ? (
            <form onSubmit={handleOrder} className="bg-gray-50 p-6 rounded-xl space-y-4">
              <h3 className="font-semibold text-lg">Place Order</h3>
              <div>
                <label className="label">Quantity ({product.unit})</label>
                <input
                  type="number"
                  value={orderQty}
                  onChange={(e) => setOrderQty(e.target.value)}
                  min={product.min_order_qty}
                  max={product.available_qty}
                  step="0.1"
                  className="input"
                  required
                />
              </div>
              
              {totalAmount > 0 && (
                <div className="bg-white p-4 rounded-lg space-y-2">
                  <div className="flex justify-between">
                    <span>Total Amount:</span>
                    <span className="font-semibold">৳{totalAmount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-primary-600">
                    <span>Pay Now (30%):</span>
                    <span className="font-semibold">৳{advanceAmount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Pay on Delivery (70%):</span>
                    <span className="font-semibold">৳{dueAmount.toFixed(2)}</span>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={createOrderMutation.isPending}
                className="w-full btn-primary py-3"
              >
                {createOrderMutation.isPending ? 'Placing Order...' : 'Place Order'}
              </button>
              <button
                type="button"
                onClick={() => setShowOrderForm(false)}
                className="w-full text-center text-gray-600 py-2"
              >
                Cancel
              </button>
            </form>
          ) : (
            <button
              onClick={() => {
                if (!isAuthenticated) navigate('/login');
                else if (user?.role !== 'buyer') alert('Only buyers can place orders');
                else setShowOrderForm(true);
              }}
              className="w-full btn-primary py-3 text-lg"
            >
              Place Order
            </button>
          )}
        </div>
      </div>
    </div>
  );
}