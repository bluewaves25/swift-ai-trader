
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PaymentForm } from "@/components/payments/PaymentForm";
import { TransactionsList } from "@/components/payments/TransactionsList";
import { PlusCircle, MinusCircle, List, ArrowLeft, Wallet, TrendingUp, CreditCard } from "lucide-react";

type PaymentView = 'main' | 'deposit' | 'withdraw' | 'transactions';

export default function InvestorPayments() {
  const [currentView, setCurrentView] = useState<PaymentView>('main');

  const renderMainView = () => (
    <div className="space-y-4 md:space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Financial Hub
        </h2>
        <p className="text-sm text-muted-foreground mt-2">
          Manage your funds and transactions securely
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <Card className="group hover:shadow-lg transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10" 
              onClick={() => setCurrentView('deposit')}>
          <CardHeader className="text-center pb-3">
            <div className="mx-auto w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <PlusCircle className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-lg font-semibold text-green-700 dark:text-green-400">
              Deposit Funds
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center pt-0">
            <p className="text-muted-foreground mb-4 text-sm">
              Add money to your trading account
            </p>
            <div className="flex items-center justify-center space-x-2 text-green-600 text-sm font-medium">
              <TrendingUp className="h-4 w-4" />
              <span>Instant Processing</span>
            </div>
          </CardContent>
        </Card>

        <Card className="group hover:shadow-lg transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/10 dark:to-rose-900/10" 
              onClick={() => setCurrentView('withdraw')}>
          <CardHeader className="text-center pb-3">
            <div className="mx-auto w-12 h-12 bg-gradient-to-r from-red-500 to-rose-600 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <MinusCircle className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-lg font-semibold text-red-700 dark:text-red-400">
              Withdraw Funds
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center pt-0">
            <p className="text-muted-foreground mb-4 text-sm">
              Transfer money to your bank account
            </p>
            <div className="flex items-center justify-center space-x-2 text-red-600 text-sm font-medium">
              <Wallet className="h-4 w-4" />
              <span>Secure Transfer</span>
            </div>
          </CardContent>
        </Card>

        <Card className="group hover:shadow-lg transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10" 
              onClick={() => setCurrentView('transactions')}>
          <CardHeader className="text-center pb-3">
            <div className="mx-auto w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <List className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-lg font-semibold text-blue-700 dark:text-blue-400">
              Transaction History
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center pt-0">
            <p className="text-muted-foreground mb-4 text-sm">
              View all your financial transactions
            </p>
            <div className="flex items-center justify-center space-x-2 text-blue-600 text-sm font-medium">
              <CreditCard className="h-4 w-4" />
              <span>Complete Records</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="mt-8 p-4 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 border">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-sm text-muted-foreground">Available Balance</p>
            <p className="text-lg font-bold text-green-600">$12,450.00</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">This Month</p>
            <p className="text-lg font-bold text-blue-600">+$2,340.00</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total Transactions</p>
            <p className="text-lg font-bold text-purple-600">47</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderView = () => {
    switch (currentView) {
      case 'deposit':
        return <PaymentForm transactionType="deposit" />;
      case 'withdraw':
        return <PaymentForm transactionType="withdrawal" />;
      case 'transactions':
        return <TransactionsList />;
      default:
        return renderMainView();
    }
  };

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {currentView !== 'main' && (
        <Button 
          variant="ghost" 
          onClick={() => setCurrentView('main')}
          className="mb-4 hover:bg-accent transition-colors duration-200"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Financial Hub
        </Button>
      )}
      
      {renderView()}
    </div>
  );
}
