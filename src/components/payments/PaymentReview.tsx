
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { PaymentMethod } from "@/services/paymentApi";

interface PaymentReviewProps {
  paymentMethod: PaymentMethod;
  amount: number;
  userDetails: any;
  onConfirm: () => void;
  onBack: () => void;
  loading?: boolean;
}

export function PaymentReview({ 
  paymentMethod, 
  amount, 
  userDetails, 
  onConfirm, 
  onBack, 
  loading 
}: PaymentReviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Review Your Deposit</CardTitle>
        <CardDescription>Please confirm your deposit details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h4 className="font-medium">Payment Details</h4>
          <div className="flex justify-between">
            <span>Amount:</span>
            <span className="font-medium">${amount}</span>
          </div>
          <div className="flex justify-between">
            <span>Payment Method:</span>
            <span className="font-medium">{paymentMethod.name} {paymentMethod.icon}</span>
          </div>
          <div className="flex justify-between">
            <span>Currency:</span>
            <span className="font-medium">USD</span>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <h4 className="font-medium">Personal Information</h4>
          <div className="flex justify-between">
            <span>Full Name:</span>
            <span className="font-medium">{userDetails.fullName}</span>
          </div>
          <div className="flex justify-between">
            <span>Phone:</span>
            <span className="font-medium">{userDetails.phoneNumber}</span>
          </div>
          <div className="flex justify-between">
            <span>Email:</span>
            <span className="font-medium">{userDetails.email}</span>
          </div>
          <div className="flex justify-between">
            <span>Date of Birth:</span>
            <span className="font-medium">{userDetails.dateOfBirth}</span>
          </div>
        </div>

        <Separator />

        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Important Notes</h4>
                          <ul className="text-xs space-y-1 text-muted-foreground">
            <li>• Your deposit will be processed within 24 hours</li>
            <li>• Funds will be available in your trading account</li>
            <li>• You can track the progress in Transactions</li>
          </ul>
        </div>

        <div className="flex space-x-4">
          <Button type="button" variant="outline" onClick={onBack} className="flex-1">
            Back to Edit
          </Button>
          <Button onClick={onConfirm} disabled={loading} className="flex-1">
            {loading ? 'Processing...' : 'Confirm Deposit'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
