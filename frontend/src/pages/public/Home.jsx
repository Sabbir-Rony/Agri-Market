import { Link } from 'react-router-dom';
import { Search, Tractor, ShoppingCart, Shield, TrendingUp } from 'lucide-react';

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Pre-Harvest Marketplace
            </h1>
            <p className="text-xl text-white/90 mb-8">
              Connect directly with farmers and secure your agricultural products before harvest. 
              Advance booking with secure split payments.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/products" className="btn-secondary text-lg px-6 py-3">
                Browse Products
              </Link>
              <Link to="/register" className="bg-white text-primary-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Join as Farmer
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Browse Products</h3>
            <p className="text-gray-600">Find pre-harvest crops from verified farmers in your area</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShoppingCart className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Book Advance</h3>
            <p className="text-gray-600">Place orders and pay 30% advance to secure your products</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Tractor className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Farmer Approval</h3>
            <p className="text-gray-600">Farmers review and approve your orders</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Secure Delivery</h3>
            <p className="text-gray-600">Pay remaining 70% on delivery with insurance protection</p>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-12 bg-white rounded-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Why Choose Us</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6">
              <TrendingUp className="w-12 h-12 text-primary-600 mb-4" />
              <h3 className="font-semibold text-xl mb-2">Direct Farmer Connection</h3>
              <p className="text-gray-600">No middlemen - connect directly with farmers and get better prices</p>
            </div>
            <div className="p-6">
              <Shield className="w-12 h-12 text-primary-600 mb-4" />
              <h3 className="font-semibold text-xl mb-2">Secure Payments</h3>
              <p className="text-gray-600">Escrow-like split payments protect both buyers and sellers</p>
            </div>
            <div className="p-6">
              <Tractor className="w-12 h-12 text-primary-600 mb-4" />
              <h3 className="font-semibold text-xl mb-2">Crop Insurance</h3>
              <p className="text-gray-600">Get compensation for crop loss due to natural disasters</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
        <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
          Join thousands of farmers and buyers already using our platform
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/register?role=farmer" className="btn-primary px-6 py-3">
            Register as Farmer
          </Link>
          <Link to="/register?role=buyer" className="btn-secondary px-6 py-3">
            Register as Buyer
          </Link>
        </div>
      </section>
    </div>
  );
}