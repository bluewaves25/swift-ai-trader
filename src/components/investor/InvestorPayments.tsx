
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import PaymentForm from "@/components/payments/PaymentForm";
import { TransactionsList } from "@/components/payments/TransactionsList";
import { PlusCircle, MinusCircle, List, ArrowLeft } from "lucide-react";

type PaymentView = 'main' | 'deposit' | 'withdraw' | 'transactions';

export default function InvestorPayments() {
  const [currentView, setCurrentView] = useState<PaymentView>('main');

  const renderMainView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Payments</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setCurrentView('deposit')}>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mb-4">
              <PlusCircle className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-lg">Deposit</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-4">Add funds to your account</p>
            <Button className="w-full">Make Deposit</Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setCurrentView('withdraw')}>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
              <MinusCircle className="h-6 w-6 text-red-600" />
            </div>
            <CardTitle className="text-lg">Withdraw</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-4">Withdraw funds from your account</p>
            <Button variant="outline" className="w-full">Make Withdrawal</Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setCurrentView('transactions')}>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-4">
              <List className="h-6 w-6 text-blue-600" />
            </div>
            <CardTitle className="text-lg">Transactions</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-4">View transaction history</p>
            <Button variant="outline" className="w-full">View History</Button>
          </CardContent>
        </Card>
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
    <div className="space-y-6">
      {currentView !== 'main' && (
        <Button 
          variant="ghost" 
          onClick={() => setCurrentView('main')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Payments
        </Button>
      )}
      
      {renderView()}
    </div>
  );
}
