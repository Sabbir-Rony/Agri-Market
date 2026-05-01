import { useState, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { productsAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { Upload, X, Image, Loader2 } from 'lucide-react';
import api from '../../services/api';

export default function AddProduct() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileInputRef = useRef(null);
  const [formData, setFormData] = useState({
    title: '',
    category: 'vegetables',
    crop_type: '',
    description: '',
    price_per_kg: '',
    min_order_qty: '',
    total_expected_qty: '',
    available_qty: '',
    unit: 'kg',
    district: '',
    upazila: '',
    expected_harvest_date: '',
    expected_delivery_date: '',
    delivery_method: 'both',
    insurance_enabled: false
  });
  
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedUrls, setUploadedUrls] = useState([]);

  const createMutation = useMutation({
    mutationFn: async (data) => {
      // First upload images if any
      let finalImages = [...uploadedUrls];
      
      if (images.length > 0) {
        setUploading(true);
        const formDataImg = new FormData();
        images.forEach(file => {
          formDataImg.append('files', file);
        });
        
        try {
          const uploadResponse = await api.post('/upload/images', formDataImg, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          
          if (uploadResponse.data.uploaded) {
            finalImages = [...uploadedUrls, ...uploadResponse.data.uploaded.map(u => u.url)];
          }
        } catch (uploadError) {
          console.error('Image upload failed:', uploadError);
        } finally {
          setUploading(false);
        }
      }
      
      // Create product with image URLs
      const productData = { ...data, images: finalImages };
      return productsAPI.create(productData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['my-products']);
      navigate('/farmer/products');
    }
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length + images.length > 10) {
      alert('Maximum 10 images allowed');
      return;
    }
    setImages([...images, ...files]);
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...formData,
      price_per_kg: parseFloat(formData.price_per_kg),
      min_order_qty: parseFloat(formData.min_order_qty),
      total_expected_qty: parseFloat(formData.total_expected_qty),
      available_qty: parseFloat(formData.available_qty),
      expected_harvest_date: formData.expected_harvest_date ? new Date(formData.expected_harvest_date).toISOString() : null,
      expected_delivery_date: formData.expected_delivery_date ? new Date(formData.expected_delivery_date).toISOString() : null
    };
    createMutation.mutate(data);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Add New Product</h1>
        <p className="text-gray-600">List your pre-harvest crops for advance booking</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-6">
        {/* Image Upload */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Product Images</h3>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="flex flex-col items-center justify-center">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageSelect}
                accept="image/*"
                multiple
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center gap-2 text-gray-600 hover:text-primary-600"
              >
                <Upload className="w-8 h-8" />
                <span>Click to upload images</span>
                <span className="text-sm text-gray-400">JPG, PNG, GIF, WebP (max 10)</span>
              </button>
            </div>
            
            {/* Image Preview */}
            {images.length > 0 && (
              <div className="mt-4 grid grid-cols-4 gap-4">
                {images.map((file, index) => (
                  <div key={index} className="relative group">
                    <div className="w-full h-24 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
                      <Image className="w-8 h-8 text-gray-400" />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <p className="text-xs text-gray-500 truncate mt-1">{file.name}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Basic Info */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Basic Information</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Product Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className="input"
                required
                placeholder="e.g., Premium Boro Rice"
              />
            </div>
            <div>
              <label className="label">Category *</label>
              <select name="category" value={formData.category} onChange={handleChange} className="input">
                <option value="vegetables">Vegetables</option>
                <option value="fruits">Fruits</option>
                <option value="grains">Grains</option>
                <option value="spices">Spices</option>
                <option value="others">Others</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Crop Type *</label>
              <input
                type="text"
                name="crop_type"
                value={formData.crop_type}
                onChange={handleChange}
                className="input"
                required
                placeholder="e.g., Rice, Potato, Tomato"
              />
            </div>
            <div>
              <label className="label">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                className="input"
                rows="2"
                placeholder="Describe your product..."
              />
            </div>
          </div>
        </div>

        {/* Pricing & Quantity */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Pricing & Quantity</h3>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="label">Price per Unit (৳) *</label>
              <input
                type="number"
                name="price_per_kg"
                value={formData.price_per_kg}
                onChange={handleChange}
                className="input"
                required
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="label">Unit</label>
              <select name="unit" value={formData.unit} onChange={handleChange} className="input">
                <option value="kg">kg</option>
                <option value="ton">ton</option>
                <option value="piece">piece</option>
              </select>
            </div>
            <div>
              <label className="label">Min Order Qty *</label>
              <input
                type="number"
                name="min_order_qty"
                value={formData.min_order_qty}
                onChange={handleChange}
                className="input"
                required
                min="1"
                placeholder="Minimum order"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Expected Total Quantity *</label>
              <input
                type="number"
                name="total_expected_qty"
                value={formData.total_expected_qty}
                onChange={handleChange}
                className="input"
                required
                min="1"
                placeholder="Expected harvest quantity"
              />
            </div>
            <div>
              <label className="label">Available for Booking *</label>
              <input
                type="number"
                name="available_qty"
                value={formData.available_qty}
                onChange={handleChange}
                className="input"
                required
                min="1"
                placeholder="Available quantity"
              />
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Location</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">District</label>
              <input
                type="text"
                name="district"
                value={formData.district}
                onChange={handleChange}
                className="input"
                placeholder="e.g., Dhaka"
              />
            </div>
            <div>
              <label className="label">Upazila</label>
              <input
                type="text"
                name="upazila"
                value={formData.upazila}
                onChange={handleChange}
                className="input"
                placeholder="e.g., Savar"
              />
            </div>
          </div>
        </div>

        {/* Dates & Delivery */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Dates & Delivery</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Expected Harvest Date</label>
              <input
                type="date"
                name="expected_harvest_date"
                value={formData.expected_harvest_date}
                onChange={handleChange}
                className="input"
              />
            </div>
            <div>
              <label className="label">Expected Delivery Date</label>
              <input
                type="date"
                name="expected_delivery_date"
                value={formData.expected_delivery_date}
                onChange={handleChange}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Delivery Method</label>
            <select name="delivery_method" value={formData.delivery_method} onChange={handleChange} className="input">
              <option value="both">Both Pickup & Delivery</option>
              <option value="pickup">Pickup Only</option>
              <option value="delivery">Delivery Only</option>
            </select>
          </div>
        </div>

        {/* Insurance */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Insurance</h3>
          
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name="insurance_enabled"
              checked={formData.insurance_enabled}
              onChange={handleChange}
              className="w-5 h-5 text-primary-600 rounded"
            />
            <div>
              <span className="font-medium">Enable Crop Insurance</span>
              <p className="text-sm text-gray-500">Buyers can claim insurance if crop is damaged</p>
            </div>
          </label>
        </div>

        {/* Submit */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={createMutation.isPending || uploading}
            className="flex-1 btn-primary py-3 flex items-center justify-center gap-2"
          >
            {(createMutation.isPending || uploading) && <Loader2 className="w-5 h-5 animate-spin" />}
            {uploading ? 'Uploading Images...' : createMutation.isPending ? 'Creating...' : 'Create Product'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/farmer/products')}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}