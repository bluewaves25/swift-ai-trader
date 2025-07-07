export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
  public: {
    Tables: {
      ai_signals: {
        Row: {
          confidence: number | null
          id: string
          signal: string | null
          symbol: string
          timestamp: string | null
        }
        Insert: {
          confidence?: number | null
          id?: string
          signal?: string | null
          symbol: string
          timestamp?: string | null
        }
        Update: {
          confidence?: number | null
          id?: string
          signal?: string | null
          symbol?: string
          timestamp?: string | null
        }
        Relationships: []
      }
      bonuses: {
        Row: {
          amount: number
          bonus_type: string
          created_at: string | null
          description: string | null
          id: string
          status: string | null
          user_id: string | null
        }
        Insert: {
          amount: number
          bonus_type: string
          created_at?: string | null
          description?: string | null
          id?: string
          status?: string | null
          user_id?: string | null
        }
        Update: {
          amount?: number
          bonus_type?: string
          created_at?: string | null
          description?: string | null
          id?: string
          status?: string | null
          user_id?: string | null
        }
        Relationships: []
      }
      fees: {
        Row: {
          amount: number
          broker: string | null
          id: string
          timestamp: string | null
          user_id: string | null
        }
        Insert: {
          amount: number
          broker?: string | null
          id?: string
          timestamp?: string | null
          user_id?: string | null
        }
        Update: {
          amount?: number
          broker?: string | null
          id?: string
          timestamp?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fees_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      losses: {
        Row: {
          amount: number
          broker: string | null
          id: string
          pair_id: string | null
          timestamp: string | null
          type: string | null
          user_id: string | null
        }
        Insert: {
          amount: number
          broker?: string | null
          id?: string
          pair_id?: string | null
          timestamp?: string | null
          type?: string | null
          user_id?: string | null
        }
        Update: {
          amount?: number
          broker?: string | null
          id?: string
          pair_id?: string | null
          timestamp?: string | null
          type?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "losses_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "losses_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      market_data: {
        Row: {
          close: number | null
          high: number | null
          id: string
          low: number | null
          open: number | null
          symbol: string
          timestamp: string | null
          volume: number | null
        }
        Insert: {
          close?: number | null
          high?: number | null
          id?: string
          low?: number | null
          open?: number | null
          symbol: string
          timestamp?: string | null
          volume?: number | null
        }
        Update: {
          close?: number | null
          high?: number | null
          id?: string
          low?: number | null
          open?: number | null
          symbol?: string
          timestamp?: string | null
          volume?: number | null
        }
        Relationships: []
      }
      pair_strategies: {
        Row: {
          created_at: string | null
          id: string
          pair_id: string | null
          strategy: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          pair_id?: string | null
          strategy: string
        }
        Update: {
          created_at?: string | null
          id?: string
          pair_id?: string | null
          strategy?: string
        }
        Relationships: [
          {
            foreignKeyName: "pair_strategies_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
        ]
      }
      performance_analytics: {
        Row: {
          id: string
          profit_loss: number | null
          strategy: string
          timestamp: string | null
          user_id: string | null
          win_rate: number | null
        }
        Insert: {
          id?: string
          profit_loss?: number | null
          strategy: string
          timestamp?: string | null
          user_id?: string | null
          win_rate?: number | null
        }
        Update: {
          id?: string
          profit_loss?: number | null
          strategy?: string
          timestamp?: string | null
          user_id?: string | null
          win_rate?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "performance_analytics_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      portfolios: {
        Row: {
          available_balance: number | null
          broker: string | null
          created_at: string | null
          id: string
          invested_amount: number | null
          realized_pnl: number | null
          total_balance: number | null
          unrealized_pnl: number | null
          user_id: string | null
        }
        Insert: {
          available_balance?: number | null
          broker?: string | null
          created_at?: string | null
          id?: string
          invested_amount?: number | null
          realized_pnl?: number | null
          total_balance?: number | null
          unrealized_pnl?: number | null
          user_id?: string | null
        }
        Update: {
          available_balance?: number | null
          broker?: string | null
          created_at?: string | null
          id?: string
          invested_amount?: number | null
          realized_pnl?: number | null
          total_balance?: number | null
          unrealized_pnl?: number | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "portfolios_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string | null
          date_of_birth: string | null
          full_name: string | null
          id: string
          name: string | null
          phone_number: string | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          date_of_birth?: string | null
          full_name?: string | null
          id?: string
          name?: string | null
          phone_number?: string | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          date_of_birth?: string | null
          full_name?: string | null
          id?: string
          name?: string | null
          phone_number?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "profiles_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      risk_settings: {
        Row: {
          created_at: string | null
          id: string
          max_loss: number | null
          max_position_size: number | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          max_loss?: number | null
          max_position_size?: number | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          max_loss?: number | null
          max_position_size?: number | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "risk_settings_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      subscriptions: {
        Row: {
          created_at: string | null
          id: string
          renewal_date: string
          status: string | null
          tier: string
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          renewal_date: string
          status?: string | null
          tier: string
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          renewal_date?: string
          status?: string | null
          tier?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "subscriptions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      support_tickets: {
        Row: {
          created_at: string | null
          description: string
          id: string
          status: string | null
          subject: string
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          description: string
          id?: string
          status?: string | null
          subject: string
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          description?: string
          id?: string
          status?: string | null
          subject?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "support_tickets_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      system: {
        Row: {
          id: number
          trading_active: boolean
          updated_at: string | null
        }
        Insert: {
          id?: number
          trading_active?: boolean
          updated_at?: string | null
        }
        Update: {
          id?: number
          trading_active?: boolean
          updated_at?: string | null
        }
        Relationships: []
      }
      trades: {
        Row: {
          account_number: string
          broker: string | null
          id: string
          order_id: string | null
          pair_id: string | null
          price: number
          side: string | null
          status: string | null
          stop_loss: number | null
          symbol: string
          take_profit: number | null
          timestamp: string | null
          user_id: string | null
          volume: number
        }
        Insert: {
          account_number: string
          broker?: string | null
          id?: string
          order_id?: string | null
          pair_id?: string | null
          price: number
          side?: string | null
          status?: string | null
          stop_loss?: number | null
          symbol: string
          take_profit?: number | null
          timestamp?: string | null
          user_id?: string | null
          volume: number
        }
        Update: {
          account_number?: string
          broker?: string | null
          id?: string
          order_id?: string | null
          pair_id?: string | null
          price?: number
          side?: string | null
          status?: string | null
          stop_loss?: number | null
          symbol?: string
          take_profit?: number | null
          timestamp?: string | null
          user_id?: string | null
          volume?: number
        }
        Relationships: [
          {
            foreignKeyName: "trades_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "trades_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      trading_pairs: {
        Row: {
          base_asset: string
          broker: string | null
          created_at: string | null
          id: string
          quote_asset: string
          symbol: string
        }
        Insert: {
          base_asset: string
          broker?: string | null
          created_at?: string | null
          id?: string
          quote_asset: string
          symbol: string
        }
        Update: {
          base_asset?: string
          broker?: string | null
          created_at?: string | null
          id?: string
          quote_asset?: string
          symbol?: string
        }
        Relationships: []
      }
      transaction_steps: {
        Row: {
          completed_at: string | null
          created_at: string | null
          id: string
          notes: string | null
          status: string | null
          step_name: string
          transaction_id: string | null
        }
        Insert: {
          completed_at?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          status?: string | null
          step_name: string
          transaction_id?: string | null
        }
        Update: {
          completed_at?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          status?: string | null
          step_name?: string
          transaction_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "transaction_steps_transaction_id_fkey"
            columns: ["transaction_id"]
            isOneToOne: false
            referencedRelation: "transactions"
            referencedColumns: ["id"]
          },
        ]
      }
      transactions: {
        Row: {
          amount: number
          broker: string | null
          created_at: string | null
          currency: string
          description: string | null
          failure_reason: string | null
          id: string
          method: string | null
          payment_method: string | null
          provider_transaction_id: string | null
          status: string | null
          timestamp: string | null
          type: string | null
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          amount: number
          broker?: string | null
          created_at?: string | null
          currency: string
          description?: string | null
          failure_reason?: string | null
          id?: string
          method?: string | null
          payment_method?: string | null
          provider_transaction_id?: string | null
          status?: string | null
          timestamp?: string | null
          type?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          amount?: number
          broker?: string | null
          created_at?: string | null
          currency?: string
          description?: string | null
          failure_reason?: string | null
          id?: string
          method?: string | null
          payment_method?: string | null
          provider_transaction_id?: string | null
          status?: string | null
          timestamp?: string | null
          type?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "transactions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      user_settings: {
        Row: {
          created_at: string | null
          id: string
          notifications: boolean | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          notifications?: boolean | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          notifications?: boolean | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "user_settings_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      users: {
        Row: {
          created_at: string | null
          email: string
          id: string
          is_admin: boolean | null
          role: string | null
        }
        Insert: {
          created_at?: string | null
          email: string
          id?: string
          is_admin?: boolean | null
          role?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string
          id?: string
          is_admin?: boolean | null
          role?: string | null
        }
        Relationships: []
      }
      wallets: {
        Row: {
          account_number: string
          balance: number
          broker: string | null
          created_at: string | null
          currency: string
          id: string
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          account_number: string
          balance?: number
          broker?: string | null
          created_at?: string | null
          currency: string
          id?: string
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          account_number?: string
          balance?: number
          broker?: string | null
          created_at?: string | null
          currency?: string
          id?: string
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "wallets_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      withdrawals: {
        Row: {
          account_number: string
          address: string
          amount: number
          broker: string | null
          created_at: string | null
          currency: string
          id: string
          status: string | null
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          account_number: string
          address: string
          amount: number
          broker?: string | null
          created_at?: string | null
          currency: string
          id?: string
          status?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          account_number?: string
          address?: string
          amount?: number
          broker?: string | null
          created_at?: string | null
          currency?: string
          id?: string
          status?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "withdrawals_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      create_transaction_steps: {
        Args: { p_transaction_id: string; p_transaction_type: string }
        Returns: undefined
      }
      update_portfolio_balance: {
        Args: {
          p_user_id: string
          p_amount: number
          p_transaction_type: string
        }
        Returns: undefined
      }
    }
    Enums: {
      market_condition: "trending_up" | "trending_down" | "ranging" | "volatile"
      signal_type: "buy" | "sell" | "hold"
      strategy_type:
        | "breakout"
        | "mean_reversion"
        | "momentum"
        | "scalping"
        | "grid"
      trade_status: "pending" | "executed" | "cancelled" | "failed"
      trade_type: "buy" | "sell"
      user_role: "owner" | "investor"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      market_condition: ["trending_up", "trending_down", "ranging", "volatile"],
      signal_type: ["buy", "sell", "hold"],
      strategy_type: [
        "breakout",
        "mean_reversion",
        "momentum",
        "scalping",
        "grid",
      ],
      trade_status: ["pending", "executed", "cancelled", "failed"],
      trade_type: ["buy", "sell"],
      user_role: ["owner", "investor"],
    },
  },
} as const
