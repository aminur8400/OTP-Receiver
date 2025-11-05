<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use App\Models\PaymentMethod;

class ProfileController extends Controller
{
    public function show(Request $r){
        return response()->json($r->user());
    }

    public function updateProfile(Request $r){
        $r->validate([
            'name'=>'nullable|string',
            'phone'=>'nullable|string',
            'dob'=>'nullable|date',
        ]);
        $user = $r->user();
        $user->fill($r->only('name','phone','dob'));
        $user->save();
        return response()->json($user);
    }

    public function changePassword(Request $r){
        $r->validate(['old_password'=>'required','password'=>'required|min:6|confirmed']);
        $user = $r->user();
        if(!Hash::check($r->old_password, $user->password)){
            return response()->json(['error'=>'Invalid old password'],422);
        }
        $user->password = Hash::make($r->password);
        $user->save();
        return response()->json(['ok'=>true]);
    }

    public function addPaymentMethod(Request $r){
        $r->validate(['method_type'=>'required|string','details'=>'required|string']);
        $pm = $r->user()->payments()->create($r->only('method_type','details','is_default'));
        if($r->filled('is_default') && $r->is_default){
            // unset other defaults
            $r->user()->payments()->where('id','<>',$pm->id)->update(['is_default'=>false]);
        }
        return response()->json($pm);
    }

    public function listPaymentMethods(Request $r){
        return response()->json($r->user()->payments()->get());
    }
}
