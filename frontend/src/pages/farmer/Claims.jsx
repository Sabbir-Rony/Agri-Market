import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { claimsAPI, productsAPI } from '../../services/api';
import { Shield, Plus, Eye } from 'lucide-react';

export default function FarmerClaims() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    product_id: '',
    cause: 'flood',
    damage_quantity: '',
    estimated_loss: '',
    description: ''
  });

  const { data: claims, isLoading } = useQuery({
    queryKey: ['my-claims'],
    queryFn: () => claimsAPI.my().then(res => res.data)
  });

  const { data: products } = useQuery({
    queryKey: ['insurable-products'],
    queryFn: () => productsAPI.myProducts().then(res => res.data)
  });

  const createMutation = useMutation({
    mutationFn: (data) => claimsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['my-claims']);
      setShowForm(false);
      setFormData({
        product_id: '',
        cause: 'flood',
        damage_quantity: '',
        estimated_loss: '',
        description: ''
      });
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate({
      ...formData,
      damage_quantity: parseFloat(formData.damage_quantity),
      estimated_loss: parseFloat(formData.estimated_loss)
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'claim_opened': 'bg-yellow-100 text-yellow-700',
      'claim_reviewing': 'bg-blue-100 text-blue-700',
      'claim_approved': 'bg-green-100 text-green-700',
      'claim_rejected': 'bg-red-100 text-red-700',
      'paid': 'bg-purple-100 text-purple-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Insurance Claims</h1>
          <p className="text-gray-600">Submit and track crop loss claims</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Claim
        </button>
      </div>

      {/* Claim Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          <h3 className="font-semibold text-lg">Submit New Claim</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Product *</label>
              <select
                name="product_id"
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                className="input"
                required
              >
                <option value="">Select product</option>
                {products?.filter(p => p.insurance_enabled).map(p => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Cause of Damage *</label>
              <select
                name="cause"
                value={formData.cause}
                onChange={(e) => setFormData({ ...formData, cause: e.target.value })}
                className="input"
              >
                <option value="flood">Flood</option>
                <option value="drought">Drought</option>
                <option value="disease">Disease</option>
                <option value="pest">Pest Attack</option>
                <option value="fire">Fire</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Damaged Quantity *</label>
              <input
                type="number"
                name="damage_quantity"
                value={formData.damage_quantity}
                onChange={(e) => setFormData({ ...formData, damage_quantity: e.target.value })}
                className="input"
                required
                min="1"
                placeholder="kg"
              />
            </div>
            <div>
              <label className="label">Estimated Loss (৳) *</label>
              <input
                type="number"
                name="estimated_loss"
                value={formData.estimated_loss}
                onChange={(e) => setFormData({ ...formData, estimated_loss: e.target.value })}
                className="input"
                required
                min="1"
                placeholder="Estimated financial loss"
              />
            </div>
          </div>

          <div>
            <label className="label">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows="3"
              placeholder="Describe the damage..."
            />
          </div>

          <div className="flex gap-4">
            <button type="submit" disabled={createMutation.isPending} className="btn-primary">
              {createMutation.isPending ? 'Submitting...' : 'Submit Claim'}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg">
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Claims List */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="font-semibold text-lg mb-4">My Claims</h2>
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
          </div>
        ) : claims?.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No claims submitted yet</p>
        ) : (
          <div className="space-y-4">
            {claims?.map(claim => (
              <div key={claim.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{claim.claim_number}</p>
                    <p className="text-sm text-gray-600">Product: {claim.product_title}</p>
                    <p className="text-sm text-gray-600">Cause: {claim.cause}</p>
                    <p className="text-sm text-gray-600">
                      Damage: {claim.damage_quantity} kg | Loss: ৳{claim.estimated_loss}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Submitted: {new Date(claim.submitted_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(claim.status)}`}>
                    {claim.status.replace(/_/g, ' ')}
                  </span>
                </div>
                {claim.payout_amount && (
                  <div className="mt-2 text-sm text-green-600">
                    Payout: ৳{claim.payout_amount}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}