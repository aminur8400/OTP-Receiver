<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Withdrawal extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'points', 'amount', 'status', 'note'
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
