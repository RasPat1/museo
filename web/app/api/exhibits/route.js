import { NextResponse } from "next/server";
import { getExhibits } from "@/lib/db";

export async function GET(request) {
    try {
        const { searchParams } = new URL(request.url);
        const museumIds = searchParams.get("museums")
            ? searchParams.get("museums").split(",")
            : [];
        const search = searchParams.get("search") || "";

        const exhibits = getExhibits({ museumIds, search });
        return NextResponse.json(exhibits);
    } catch (error) {
        console.error("Exhibits API error:", error);
        return NextResponse.json(
            { error: "Failed to load exhibits" },
            { status: 500 }
        );
    }
}
