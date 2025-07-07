
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PaymentMethod, paymentMethods } from "@/services/paymentApi";

interface PaymentMethodSelectorProps {
  onSelect: (method: PaymentMethod) => void;
  selectedMethod?: PaymentMethod;
}

export function PaymentMethodSelector({ onSelect, selectedMethod }: PaymentMethodSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Select Payment Method</CardTitle>
        <CardDescription>Choose how you'd like to make your deposit</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {paymentMethods.map((method) => (
            <Button
              key={method.id}
              variant={selectedMethod?.id === method.id ? "default" : "outline"}
              className="h-20 flex flex-col items-center space-y-2"
              onClick={() => onSelect(method)}
            >
              <span className="text-2xl">{method.icon}</span>
              <span className="text-sm">{method.name}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
